import os, sys, getpass
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from seleniumrequests import Chrome, Firefox
import requests
import time
from config import user_email, user_password, google_form_link_base
from datetime import datetime
import json
from bidrl_classes import Item, Invoice, Auction



def login_try_loop(browser, user):
    browser.get('https://www.bidrl.com/login')
    time.sleep(0.5)
    try:
        userName = browser.find_element(By.NAME, 'username')
        password = browser.find_element(By.NAME, 'password')

        #put all elements with tag name "button" into a list
        button_elements = browser.find_elements(By.TAG_NAME, 'button')
        #find the first element in the button_elements list with text 'LOGIN'
        login_button = next(obj for obj in button_elements if obj.text == 'LOGIN')

        actions = ActionChains(browser)
        actions.move_to_element(userName).send_keys(user['name'])
        actions.send_keys(Keys.TAB).send_keys(user['pw'])
        actions.move_to_element(login_button).click()

        print("Attempting to log in using: " + user['name'])
        actions.perform()
    except:
        login_try_loop(browser, user)
    print("login success")
    return


# initialize webdriver object with Chrome. if not headless, set size and position
def init_webdriver_chrome(headless = ''):
    if headless == 'headless':
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        #chrome_options.add_argument("--log-level=3")
        browser = Chrome(options=chrome_options) # initialize chrome browser webdriver using seleniumrequests library using headless chrome options
        print('Chrome webdriver initialized in headless mode')
    else:
        browser = Chrome() # initialize chrome browser webdriver using seleniumrequests library
        print('Chrome webdriver initialized')
        browser.set_window_position(0, 0)
        browser.maximize_window()
    return browser


# go to favorites page, set records per page to records_per_page. can specify to hide or show closed items
def load_page_favorites(browser, records_per_page, hide_or_show = 'hide'):
    time.sleep(1) # seems to be needed. tried to fix in various ways and this is one that worked consistently
    browser.get('https://www.bidrl.com/myaccount/myitems/' + hide_or_show + '_closed/')
    # we want to attempt to set "Records per page" drop down to 60, but sometimes there is only one page and the button doesn't exist
    # attempt to find the button and move on if we cannot
    time.sleep(1)
    try:
        perpage = browser.find_element(By.ID, 'perpage-top')
        actions = ActionChains(browser)
        actions.move_to_element(perpage).click()
        actions.send_keys(str(records_per_page))
        actions.send_keys(Keys.ENTER)
        actions.perform()
    except:
        print("load_page_favorites: no records per page button found. continuing")
    return



# go to invoices page, set records per page to 36
def load_page_invoices(browser, records_per_page):
    print("Loading https://www.bidrl.com/myaccount/invoices")
    time.sleep(1) # seems to be needed. tried to fix in various ways and this is one that worked consistently
    browser.get('https://www.bidrl.com/myaccount/invoices')
    time.sleep(1)
    perpage = browser.find_element(By.ID, 'perpage-top')
    actions = ActionChains(browser)
    actions.move_to_element(perpage).click()
    actions.send_keys(str(records_per_page))
    actions.send_keys(Keys.ENTER)
    actions.perform()



# requires: a logged in web driver, a list of invoice links, a date object indicating the furthest back date of invoice we want to scrape
# returns: a list of Invoice objects (one for each invoice in the link list)
# maybe we do better later with a GET request to pull the html response, and then put it through an html parser like beautifulsoup's
# but for now this works
def scrape_invoices(browser, invoice_link_list, start_date):
    invoices = []  # list of Invoice objects to return at the end

    for link in invoice_link_list:
        print("going to: " + link)
        browser.get(link) # go to invoice link
        time.sleep(0.5)

        # information we want to extract for current invoice
        invoice_date = ''
        invoice_num = ''
        invoice_items = []  # This will hold instances of the Item class

        # gather list of all elements with tag name "tr"
        # sometimes no tr elements are found. I don't know why. but if that's the case, keep reloading the page and trying again
        # time out after 5 tries
        tr_elements = browser.find_elements(By.TAG_NAME, 'tr')
        timeout = 0
        while len(tr_elements) == 0 and timeout <= 5:
            print('no tr elements found. reloading')
            browser.get(link)
            time.sleep(0.5)
            tr_elements = browser.find_elements(By.TAG_NAME, 'tr')
            timeout += 1

        # iterate through gathered tr elements to extract information
        for tr in tr_elements: # each tr element is an item row

            # split up text, search through it to find "Date: " and "Invoice: " and extract date and invoice num if found
            for line in tr.text.split('\n'):
                if "Date: " in line:
                    invoice_date = line.split("Date: ")[1]
                if "Invoice: " in line:
                    invoice_num = line.split("Invoice: ")[1]

            # Initialize an empty dictionary to temporarily hold item details
            temp_item_dict = {'id': '', 'description': '', 'tax_rate': '', 'current_bid': '', 'url': ''}

            # get all td elements in row, then iterate through. these are the Lot and Description columns, and where we'll find the item link
            td_elements = tr.find_elements(By.TAG_NAME, 'td')
            if len(td_elements) == 2:
                temp_item_dict['id'] = td_elements[0].text
                temp_item_dict['description'] = td_elements[1].text
                try:
                    temp_item_dict['url'] = td_elements[1].find_element(By.TAG_NAME, 'a').get_property('href')
                except:
                    continue

            # get all th elements in row, then iterate through. these are the Tax Rate and Amount columns
            th_elements = tr.find_elements(By.TAG_NAME, 'th')
            if len(th_elements) == 2:
                temp_item_dict['tax_rate'] = th_elements[0].text
                temp_item_dict['current_bid'] = th_elements[1].text

            # add scraped item if description is populated and the first value scraped isn't 'Print View'. this trashes the first garbage "item" scraped
            if temp_item_dict['description'] and temp_item_dict['id'] != 'Print View':
                #print(temp_item_dict)
                invoice_items.append(Item(**temp_item_dict))

        print('invoice date: ' + invoice_date)
        try:
            invoice_date_obj = datetime.strptime(invoice_date, '%m/%d/%Y')
            if invoice_date_obj < start_date:
                print('encountered earlier date. breaking')
                break
        except:
            print('exception. failed to parse read invoice date as date object')
            continue

        # Create an Invoice instance and add it to the invoices list
        new_invoice = Invoice(id=invoice_num, date=invoice_date, link=link, items=invoice_items)
        invoices.append(new_invoice)
    
    return invoices


'''def gigascrape_old():
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
    conn = bf.init_sqlite_connection()
    cursor = conn.cursor()

    # send browser to bidrl.com. this gets us the cookies we need to send the POST requests properly next
    browser.get('https://www.bidrl.com')

    post_url = "https://www.bidrl.com/api/auctions"

    # get list of date intervals to pull auctions from
    # can only pull a max of 1 year at a time
    dates = bf.generate_date_intervals_for_auction_scrape()
    for date in dates:
        start_date = date['start_date'].strftime("%Y-%m-%d")
        end_date = date['end_date'].strftime("%Y-%m-%d")
        print(f"\nAuction pull date range: {start_date} to {end_date}")

        post_data = {
            "filters[startDate]": start_date
            , "filters[endDate]": end_date
            , "filters[perpage]": 10000
            , "past_sales": "true"
            , "filters[affiliates]": 47
        }

        print("Attempting to get response from POST request to https://www.bidrl.com/api/auctions")
        start_time = time.time()
        response = browser.request('POST', post_url, data=post_data) # send the POST request with the session that contains the cookies
        end_time = time.time()
        response.raise_for_status() # ensure the request was successful
        print("Response recieved! Time taken: " + str(end_time - start_time))
        auction_json = response.json()

        # only execute the rest of the contents of this loop if result == 'success'
        # meaning we recieved auction json properly
        if auction_json['result'] == 'success':
            auction_data_json = auction_json['data']
            print("Number of auctions recieved: " + str(len(auction_data_json)))
        elif auction_json['code'] == 'NO_AUCTION_LIST':
            print("No auctions found for this date range.")
            continue
        else:
            print("\n\nRecieved response that wasn't 'success'. Add it to the if/else ladder in gigascrape():\n\n")
            print(auction_json)
            quit()

        # get auction_ids from sql so we can skip scraping auctions that have already been scraped
        cursor.execute("SELECT auction_id FROM auctions")
        auctions_in_db = cursor.fetchall()
        # extract auction_id from each row and store in a list
        auctions_in_db_list = [auction['auction_id'] for auction in auctions_in_db]

        for auction in auction_data_json:
            # check if auction_id we are about to scrape has already been scraped. skip if so
            if auction['id'] in auctions_in_db_list:
                print(f"Auction {auction['id']} already exists in the database. Skipping.")
                continue

            # skip if auction is not a real auction
            if auction['item_count'] == '0':
                print(f"Auction item_count = 0. Concluding not a real auction and skipping.")
                continue

            auction_url = "https://www.bidrl.com/auction/" + auction['auction_id_slug'] + "/bidgallery/"

            print("\nScraping item urls from: " + auction_url)
            item_urls = bf.get_auction_item_urls(auction_url)
            print(str(len(item_urls)) + " items found")

            # remove any item urls that end with '/i/'
            # track items_removed so that verification function doesn't get tripped up
            # ex: the "I <3 ZACH T-Shirt 2XL" item in this auction:
                # https://www.bidrl.com/auction/high-end-auction-161-johns-rd-unit-a-south-carolina-december-10-143518/bidgallery/perpage_NjA/page_Mg
            items_removed = 0
            for url in item_urls[:]:  # Use a slice copy to iterate over while modifying the original list
                if url.endswith("/i/"):
                    item_urls.remove(url)
                    items_removed += 1
                    print(f"Removed URL ending with '/i/': {url}")

            print("Scraping item info")
            items = bf.get_items(item_urls, browser)


            # auction object to hold all of our auction data before we insert it into the sql database
            auction_obj = Auction(
                id=auction['id'],
                url=auction_url,
                items=items,
                title=auction['title'],
                item_count=int(auction['item_count']),
                start_datetime=auction['starts'],
                status=auction['status'],
                affiliate_id=auction['affiliate_id'],
                aff_company_name=auction['aff_company_name'],
                state_abbreviation=auction['state_abbreviation'].strip(),
                city=auction['city'],
                zip=auction['zip'],
                address=auction['address']
            )

            if verify_auction_object_complete(auction_obj, items_removed) == False:
                print("Auction did not pass verification! Not adding to sql database. Exiting program.")
                quit()
            else:
                print("Auction object passed verification. Attempting to add to sql database.")
                if bf.insert_entire_auction_to_sql_db(conn, auction_obj) == 0:
                    print("Successfully added to database.")
                else:
                    print("Failed to add to database. Exiting.")
                    quit()
    
    browser.quit()'''


# get auctions list
# requires:
    # name of affiliate "company". ex: 'south-carolina'. defaults to sc
    # webdriver object. if webdriver object has been logged in as a user, then the attribute is_favorite will be filled in for items
# returns: list of Auction objects
def get_open_auctions(browser, affiliate_company_name = 'south-carolina', debug = 'false'):
    get_url = "https://www.bidrl.com/api/landingPage/" + affiliate_company_name

    response = browser.request('GET', get_url) # make the GET request

    if response.status_code == 200: # check if the request was successful

        response_json = response.json()
        #print(f"JSON recieved. total auctions: {response_json['total']}")

        # get list of number ids for each auction listed in the JSON
        auctions_num_list = []
        for auction in response_json['auctions']:
            auctions_num_list.append(auction)

        if debug == 'true':
           # FOR DEBUGGING. causes function to only scrape first auction
           auctions_num_list = auctions_num_list[0]

        # loop through each auction by number in the json and extract information to an Auction object
        auctions = []
        for auction_num in auctions_num_list:
            auction_json = response_json['auctions'][auction_num]

            auction_url = "https://www.bidrl.com/auction/" + auction_json['auction_id_slug'] + "/bidgallery/"

            print("\nscraping item urls from: " + auction_url)
            item_urls = get_auction_item_urls(auction_url)
            print(str(len(item_urls)) + " items found")

            print("scraping item info")
            items = get_items(item_urls, browser)

            # dictionary to temporarily hold auction details before creating object
            temp_auction_dict = {'id': auction_json['id']
                                    , 'url': auction_url
                                    , 'items': items
                                    , 'title': auction_json['title']
                                    , 'item_count': int(auction_json['item_count'])
                                    , 'start_datetime': auction_json['starts']
                                    , 'status': auction_json['status']
                                    , 'affiliate_id': response_json['affiliate']['affiliate_id']
                                    , 'aff_company_name': response_json['affiliate']['aff_company_name']
                                    , 'state_abbreviation': auction_json['state_abbreviation'].strip()
                                    , 'city': auction_json['city']
                                    , 'zip': auction_json['zip']
                                    , 'address': auction_json['address']
                                }
            
            # instantiate Autcion object with info from temp_auction_dict and add to list
            auctions.append(Auction(**temp_auction_dict))

        return auctions
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return 1
    
# get item data from a list of item URLS
# requires: list of item URLs, webdriver object, and an optional specification to get bid history or not
# returns: list of Item objects
def get_items(item_urls, browser, get_bid_history = 'true'):
    items = [] # list to fill with item objects and return at end
    for item_url in item_urls:
        extracted_ids = extract_ids_from_item_url(item_url) # extract auction id and item id from url
        
        item_obj = get_item_with_ids(browser
                                     , extracted_ids['item_id']
                                     , extracted_ids['auction_id']
                                     , get_bid_history)
        items.append(item_obj)

        print(f"get_items() scraped: {item_obj.description} (with {len(item_obj.bids)} bids)")
    return items


# get list of item urls from an auction
# requires URL in this format:
# https://www.bidrl.com/auction/outdoor-sports-auction-161-johns-rd-unit-a-south-carolina-april-25-152770/bidgallery/
# returns: list of urls, one for each item in the auction provided
def get_auction_item_urls(auction_url):
    auction_id = extract_id_from_auction_url(auction_url)['auction_id'] # extract auction id from url

    session = requests.Session() # create a session object to persist cookies
    response = session.get(auction_url) # make a GET request to get the cookies
    post_url = "https://www.bidrl.com/api/getitems"

    # set items per page to 10k to ensure we capture all item urls in auction
    # this prevents us from having to loop through pages with attribute filters[page]
    post_data = {"auction_id": auction_id
                 , "filters[perpage]": 10000
                 , "show_closed": "closed"
                 , "item_type": "itemlist"}
    response = session.post(post_url, data=post_data)
    response.raise_for_status() # ensure the request was successful

    #print(response.json())

    item_urls = [] # list for item urls to return
    for item in response.json()['items']:
        item_urls.append(item['item_url'])

    return item_urls



'''# scrape item objects from bidrl based on list of item_id/auction_id read in from csv.
# we do this because we want the most up-to-date information for these items, like end_time_unix
def scrape_item_objects_from_rows(browser, item_rows_list):
    print("Scraping item objects based on item_id and auction_id read from csv.")
    try:
      item_list = [] # list for item objects to return at the end
      for item_num, item_row in enumerate(item_rows_list):
          item_obj = bf.get_item_with_ids(browser, item_row['item_id'], item_row['auction_id'], get_bid_history = 'false')

          # check if max_desired_bid is not empty. if it isn't, then convert to float. if it is, then set to None
          item_obj.max_desired_bid = float(item_row['max_desired_bid']) if item_row['max_desired_bid'] != '' else None

          print(f"Item object scraped ({item_num + 1}/{len(item_rows_list)}): {item_obj.description}")
          item_list.append(item_obj)
      return item_list
    except Exception as e:
        print(f"scrape_item_objects_from_rows() failed with exception: {e}")
        print("Tearing down web object.")
        browser.quit()
        return 1'''


'''# read favorite_items_to_input_max_bid.csv and return list of item objects for items where max_desired_bid > 0
def read_user_input_csv(browser):
    try:
        filename = 'favorite_items_to_input_max_bid.csv'
        path_to_file = 'local_files/'

        file_path = path_to_file + filename

        fieldnames = ['end_time_unix', 'auction_id', 'item_id', 'description', 'max_desired_bid', 'url']

        read_rows = bf.read_items_from_csv(file_path, fieldnames)

        #item_list = scrape_item_objects_from_rows(browser, read_rows)
        item_list = create_item_objects_from_rows(read_rows)

        items_to_bid_on = []
        item_count_with_desired_bid = 0
        item_count_zero_desired_bid = 0
        item_count_no_desired_bid = 0
        item_count_already_closed = 0
        for item in item_list:
            if item.max_desired_bid == 0:
                item_count_zero_desired_bid += 1
            elif item.max_desired_bid == None:
                item_count_no_desired_bid += 1
            else:
                item_count_with_desired_bid += 1
                if item.bidding_status == 'Closed':
                    item_count_already_closed += 1
                else:
                    items_to_bid_on.append(item)

        print(f"\nRead file: {filename}.")
        print(f"Items with max_desired_bid: {item_count_with_desired_bid}")
        print(f"Items with max_desired_bid that already closed: {item_count_already_closed}")
        print(f"Items without max_desired_bid: {item_count_no_desired_bid}")
        print(f"Items with 0 max_desired_bid: {item_count_zero_desired_bid}\n")

        # sort list of items in descending order based on their end time
        items_to_bid_on.sort(key=lambda x: x.end_time_unix, reverse=True)

        return items_to_bid_on
    except Exception as e:
        print(f"read_user_input_csv() failed with exception: {e}")
        print("Tearing down web object.")
        browser.quit()
        return 1'''
    


# requires: auction_id of the auction from which we want to gather the item ids
# returns: list of item ids given an auction id
def scrape_item_id_list_from_auction(auction_id):
    session = requests.Session() # create a session object to persist cookies
    response = session.get('https://www.bidrl.com/') # make a GET request to get cookies
    post_url = "https://www.bidrl.com/api/getitems"

    # set items per page to 10k to ensure we capture all items in auction
    post_data = {"auction_id": auction_id
                 , "filters[perpage]": 10000
                 , "show_closed": "closed"
                 , "item_type": "itemlist"}
    response = session.post(post_url, data=post_data)
    response.raise_for_status() # ensure the request was successful

    item_ids = []
    for item in response.json()['items']:
        item_ids.append(item['id'])
    
    return item_ids


# requires: webdriver object, auction_id
# returns: list of fully populated item objects for that auction
def scrape_items_old(browser, auction_id):
    item_ids = scrape_item_id_list_from_auction(auction_id)
    print(f"Scraping items from auction with id: {auction_id}.")
    items = []
    for item_id in item_ids:
        items.append(get_item_with_ids(browser, item_id, auction_id))
    return items