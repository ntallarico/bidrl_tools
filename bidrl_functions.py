import os, sys, getpass, time, re, json, csv, requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from seleniumrequests import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from bidrl_classes import Item, Invoice, Auction, Bid, Affiliate, Image
from bs4 import BeautifulSoup
import pyodbc
import sqlite3
#from config import user_email, user_password, google_form_link_base, sql_server_name, sql_database_name, sql_admin_username, sql_admin_password


def init_webdriver(headless = ''):
    if headless == 'headless':
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        browser = Firefox(options=firefox_options) # initialize Firefox browser webdriver using seleniumrequests library using headless Firefox options
        print('Firefox webdriver initialized in headless mode')
    else:
        browser = Firefox() # initialize Firefox browser webdriver using seleniumrequests library
        print('Firefox webdriver initialized')
        browser.set_window_position(0, 0)
        browser.maximize_window()
    return browser


# attempt to load and log in to bidrl
def try_login(browser, login_name, login_password):
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
        actions.move_to_element(userName).send_keys(login_name)
        actions.send_keys(Keys.TAB).send_keys(login_password)
        actions.move_to_element(login_button).click()
        actions.perform()
        time.sleep(1)
        return 0
    except:
        return 1


# returns 0 if login success, 1 if failure, and 2 if the function itself failed
# we may need a better way of determining login success at some point, but for now, this works
# as of now, if login fails the page returned starts with "<!doctype html>" instead of "<!DOCTYPE html>"
def check_if_login_success(browser):
    try:
        response = browser.request('GET', 'https://www.bidrl.com/myaccount/myitems')
        #print(response.text[0:15])
        if response.text[0:15] == '<!DOCTYPE html>':
            return 0
        else: return 1
    except Exception as e:
        print(f"check_if_login_success() failed with exception: {e}")
        return 2


# this function initializes and returns a webdriver object that has been logged in to bidrl.com with credentials supplied in config.py
def get_logged_in_webdriver(login_name, login_password, headless = ''):
    browser = init_webdriver(headless)

    attempts = 5 # number of times to attempt to login before giving up
    for n in range (1, attempts + 1):
        print(f"Attempt {n} to log in to account: {login_name}")
        try_login_result = try_login(browser, login_name, login_password) # run try_login function, set try_login_result to 0 or 1 depending on success
        if try_login_result == 1:
            print('Login failed: error in attempting to find elements of login form or execute login steps.')
            time.sleep(1)
        elif check_if_login_success(browser) == 1:
            print('Login failed: username or password incorrect.')
            time.sleep(1)
        elif check_if_login_success(browser) == 2:
            print('check_if_login_success() failed to properly complete execution.')
            time.sleep(1)
        else:
            print('Login succeeded!')
            return browser
    print(f'Gave up attempt to log in after {attempts} attempts. Exiting program.')
    browser.quit()
    quit() # exit current python script


# wait for browser to completely load webpage before moving on
# requires initialized webdriver and name of an element to wait to see
def wait_for_element_by_ID(browser, element_name):
    print(f"Waiting to see element: '{element_name}'")
    wait = WebDriverWait(browser, 10)  # Timeout after 10 seconds
    wait.until(EC.presence_of_element_located((By.ID, element_name)))
    #print("found!")


# requires: logged in webdriver, invoice URL, and a date_obj indicating the date of the earliest invoice to scrape
# returns: Invoice object
def parse_invoice_page(browser, invoice_url, earliest_invoice_date):
    # get html content returned by GET request to the invoice URL
    response = browser.request('GET', invoice_url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    # find main invoice content block
    invoice_content = soup.find('div', id="invoice-content")
    #print(invoice_content)

    items = [] # list for Item objects to add to the Invoice object

    invoice = Invoice(**{
                        'id': None,
                        'date': None,
                        'link': invoice_url,
                        'items': [],
                        'total_cost': None
                        })

    if invoice_content:
        # pull out invoice date and number
        invoice_info = invoice_content.find('tr', class_="no-borders")
        invoice_info_spans = invoice_info.find('th', style="vertical-align: bottom;").find_all('span')
        invoice.id = invoice_info_spans[0].text.strip()
        invoice.date = invoice_info_spans[1].text.strip()
        #print(f"inv id: {invoice.id}\ninv date: {invoice.date}")

        # if date of invoice is earlier than earliest_invoice_date, return nothing
        # if function is called by get_invoices(), then get_invoices() knows to then break the invoice processing loop
        invoice_date_obj = datetime.strptime(invoice.date, "%m/%d/%Y").date()
        if invoice_date_obj < earliest_invoice_date:
            return

        # loop through all tr rows and parse out items
        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) == 4:  # ensure the row has the correct number of cells
                try:
                    item_url = cells[0].find('a')['href'] if cells[0].find('a') else 'No URL'
                    item_id = cells[0].get_text(strip=True)
                    description = cells[1].get_text(strip=True)
                    tax_rate_text = cells[2].get_text(strip=True)
                    amount = cells[3].get_text(strip=True)

                     # test if item scraped is a real item
                        # ensure item_id is populated
                        # ensure item_id != 'Lot', meaning the "item" scraped is just the header row of the table
                     # then create item in Invoice's item list
                    if item_id and item_id != 'Lot':
                        invoice.items.append(Item(**{
                            'id': item_id,
                            'description': description,
                            'tax_rate': float(tax_rate_text[0:5]) * 0.01,
                            'current_bid': float(amount),
                            'url': item_url
                        }))
                    #invoice.items[len(items)-1].display() # call display function for most recent item added
                    
                except Exception as e:
                    print(f"parse_invoice_page(): Error processing row: {e}")
                    quit()
    else:
        print("Parse_invoice_page() could not find '<div id=\"invoice-content\">'. Exiting program.")
        quit()

    return invoice


# log in and pull invoices
# requires: logged in webdriver, date_obj indicating the date of the earliest invoice to scrape
# returns: list of Invoice objects
def get_invoices(browser, earliest_invoice_date):
    '''
    in GET request for invoices page, there is a string "var invoices = " followed by a list invoice dicts
    we want to extract that list string, pull out the invoice id so we can make a url for the invoice
    , then go to that url and extract all invoice and item data from it.
    we return a list of invoice objects

    the list looks like: [{'id': '3301997', ...}, {...}, {...}, ...]
    each invoice dict in the list looks like the below:
    {'id': '3301997', 'auction_group_id': '152705', 'bidder': '168516', 'number_emails_sent': '2', 'premium_rate': '13'
    , 'auction_title': 'Oversize &#38; Furniture Auction - 161 Johns Rd. Unit A -South Carolina - April 26', 'relisting_fee': None
    , 'amount_paid': '598.0000000', 'amount_paid_actual': '5.980', 'shipment_total': 0, 'sub_total': 5, 'adjustments': '0.00', 'fee_total': '0.00'
    , 'fee_tax': '0.00', 'invoice_total': '5.98', 'effective_premium': '13', 'premium': '0.65', 'total_tax': '0.33'
    , 'title': 'Auction Invoice for: Oversize &#38; Furniture Auction - 161 Johns Rd. Unit A -South Carolina - April 26', 'affiliate_id': '47'
    , 'item_count': '3', 'picked_up': '0', 'relisting_fees': None, 'auction_buyer_premium': '13.000', 'cc_not_needed': '0', 'picked_up_count': '0'
    , 'refund': '0.000000', 'effective_tax': 5.841, 'tax': 0.33, 'total': 5.98, 'balance': 0, 'init_balance': 0, 'discounted_total': 5.98, 'paid': True}
    '''

    post_data = {"perpage": 10000}
    post_url = 'https://www.bidrl.com/myaccount/invoices'
    response = browser.request('POST', post_url, data=post_data)
    response.raise_for_status() # ensure the request was successful

    # regular expression to extract the list of JSON-like objects after "var invoicesData = "
    pattern = r'var invoicesData = (\[.*?\]);'
    match = re.search(pattern, response.text)

    if match:
        # convert the matched string to a valid JSON object
        invoices_json = match.group(1)
        invoices_data = json.loads(invoices_json) # invoices_data is now a list of dicts, each for an invoice
        #print(invoices_data)

        invoices = [] # list of Invoice objects to return at the end
        for invoice in invoices_data:
            invoice_url = 'https://www.bidrl.com/myaccount/invoice/invid/' + invoice['id']
            print(f"parsing invoice at: {invoice_url}")
            invoice_obj = parse_invoice_page(browser, invoice_url, earliest_invoice_date)
            # if parse_invoice_page() returned an object, then append it to invoices list and continue
            # if not, that means earliest_invoice_date was reached, and we exit this function, returning our invoices list
            if invoice_obj: 
                invoices.append(invoice_obj)
            else:
                return invoices
        return invoices
    else:
        print("get_invoice_data(): No invoices data found. Exiting.")
        quit()


# calculates total cost of each invoice
# requires: list of Invoice objects with Amount and Tax_Rate attributes populated
# returns: nothing. alters the Invoice objects in the list and the Item objects in the lists of those Invoices
def calculate_total_cost_of_invoices(invoices):
    for invoice in invoices:
        invoice_total_cost = 0
        for item in invoice.items:
            item.total_cost = item.tax_rate + float(item.current_bid)
            invoice_total_cost += item.total_cost

        invoice.total_cost = invoice_total_cost
    return


# extract item_id and auction_id from the URL string
# returns a dictionary {'item_id': item_id, 'auction_id': auction_id}
def extract_ids_from_item_url(url):
    parts = url.split('/') # Split the URL by '/'

    item_id_segment = parts[-2] if url.endswith('/') else parts[-1]
    item_id = item_id_segment.split('-')[-1]

    auction_id_segment = parts[-4] if url.endswith('/') else parts[-3]
    auction_id = auction_id_segment.split('-')[-1]

    return {'item_id': item_id, 'auction_id': auction_id}


# extract auction_id from the URL string
# returns a dictionary {'auction_id': auction_id}
# requires URL in this format:
# https://www.bidrl.com/auction/outdoor-sports-auction-161-johns-rd-unit-a-south-carolina-april-25-152770/bidgallery/
def extract_id_from_auction_url(url):
    parts = url.split('/') # Split the URL by '/'

    auction_id_segment = parts[-3] if url.endswith('/') else parts[-3]
    auction_id = auction_id_segment.split('-')[-1]

    return {'auction_id': auction_id}


# requires instantiated webdriver, item_id, auction_id, optionally an indication to also/not scrape bids
    # and optionally an indication to also/not scrape image urls
# returns an Item object
def get_item_with_ids(browser, item_id, auction_id, get_bid_history = 'true', get_images = 'true'):
    response = browser.request('GET', 'https://www.bidrl.com/') # make GET request to get cookies

    # submit requests to API and get JSON response
    post_url = "https://www.bidrl.com/api/ItemData"
    post_data = {
        "item_id": item_id
        , "auction_id": auction_id
        , "show_closed": "closed"
    }
    response = browser.request('POST', post_url, data=post_data) # send the POST request with the session that contains the cookies
    try:
        response.raise_for_status() # ensure the request was successful
    except requests.exceptions.HTTPError as err:
        print(f"Error in get_item_with_ids(): {err}")
        print(f"post_url: {post_url}")
        print(f"post_data: {post_data}")
        browser.quit()
        quit()
    item_json = response.json()

    # if get_bid_history is set to true, then get the bid history for the item
    bids = []
    if get_bid_history == 'true':
        for bid_json in item_json['bid_history']:
            bids.append(Bid(**{
                'bid_id': bid_json['id']
                , 'item_id': item_json['id']
                , 'user_name': bid_json['user_name']
                , 'bid': float(bid_json['bid'])
                , 'bid_time': bid_json['bid_time']
                , 'time_of_bid': bid_json['time_of_bid']
                , 'time_of_bid_unix': int(bid_json['time_of_bid_unix'])
                , 'buyer_number': bid_json['buyer_number']
                , 'description': bid_json['description']
            }))
            #bids[len(bids)-1].display()

    # if get_images is set to true, then get the a list of Image objects for the item
    images = []
    if get_images == 'true':
        for image_json in item_json['images']:
            images.append(Image(**{
                'item_id': item_json['id']
                , 'image_url': image_json['image_url']
                , 'image_height': int(image_json['image_height'])
                , 'image_width': int(image_json['image_width'])
            }))

    # extract data from json into temp dictionary to create item with later
    temp_item_dict = {'id': item_json['id']
                            , 'auction_id': item_json['auction_id']
                            , 'description': item_json['title']
                            , 'tax_rate': round(float(item_json['tax_rate']) * 0.01, 4)
                            , 'buyer_premium': round(float(item_json['buyer_premium']) * 0.01, 4)
                            , 'current_bid': float(item_json['current_bid'])
                            , 'highbidder_username': item_json['highbidder_username']
                            , 'url': item_json['url']
                            , 'lot_number': item_json['lot_number']
                            , 'bidding_status': item_json['bidding_status']
                            , 'end_time_unix': int(item_json['end_time_unix']) - int(item_json['time_offset'])
                            , 'bids': bids
                            , 'bid_count': int(item_json['bid_count'])
                            , 'viewed': int(item_json['viewed'])
                            , 'images': images
                        }
    
    # can only see is_favorite key if logged in. check if it exists before attempting to add to dict
    if 'is_favorite' in item_json:
        temp_item_dict['is_favorite'] = int(item_json['is_favorite'])

    # instantiate Item object with info from temp_item_dict, print message, and return item object
    item_obj = Item(**temp_item_dict)
    #print(f"get_item_with_ids() scraped: {item_obj.description} (with {len(bids)} bids)")
    return item_obj


# get auctions list
# requires:
    # id of affiliate "company". ex: '47' for SC
    # webdriver object. if webdriver object has been logged in as a user, then the attribute is_favorite will be filled in for items
# returns: list of Auction objects
def get_open_auctions(browser, affiliate_id = '47'):
    auctions = scrape_auctions(browser, affiliate_id, auctions_to_scrape = 'open')
    for auction in auctions:
        auction.items = scrape_items(browser, auction.id)
    return auctions


# get auctions list, using scrape_items_fast (returns less info but in massively shorter time. uses /api/getitems/ on an auction_id)
# requires:
    # id of affiliate "company". ex: '47' for SC
    # webdriver object. if webdriver object has been logged in as a user, then the attribute is_favorite will be filled in for items
# returns: list of Auction objects
def get_open_auctions_fast(browser, affiliate_id = '47'):
    auctions = scrape_auctions(browser, affiliate_id, auctions_to_scrape = 'open')
    for auction in auctions:
        auction.items = scrape_items_fast(browser, auction.id)
    return auctions
    

# generates a list of dicts with start_date and end_date to use as intervals for auction scraping.
# used when setting date range filters when sending POST request to https://www.bidrl.com/api/auctions
# intervals are 1 year apart because api will only allow 1 year pull at a time
def generate_date_intervals_for_auction_scrape():
    start_date = "01/01/2008" # bidrl says they've been running since 2008
    end_date = datetime.now().strftime("%m/%d/%Y") # current day

    # Convert string dates to datetime objects
    start = datetime.strptime(start_date, "%m/%d/%Y")
    end = datetime.strptime(end_date, "%m/%d/%Y")
    
    # List to hold dicts with start and end dates of each year
    yearly_date_ranges = []
    
    current_date = start
    while current_date <= end:
        yearly_date_ranges.append({
            "start_date": current_date,
            "end_date": current_date.replace(month=12, day=31)
        })
        # Increment the date by one year
        current_date += relativedelta(years=1)
    
    return yearly_date_ranges


# requires webdriver object, affiliate_id, and optional auctions_to_scrape
# in auctions_to_scrape, specify:
    # 'all' for all historical and currently open auctions
    # 'open' for just currently open auctions
    # 'one' for just a single auction (used for debugging)
# returns list of all Auction objects 
def scrape_auctions(browser
                , affiliate_id = '47' # default to SC
                , auctions_to_scrape = 'all' # all, open, or one (for debugging)
                 ):
    
    auctions = [] # list of auctions to populate and return at the end

    # send browser to bidrl.com. this gets us the cookies we need to send the POST requests properly next
    browser.get('https://www.bidrl.com')

    post_url = "https://www.bidrl.com/api/auctions"

    # get list of date intervals to pull auctions from
    # can only pull a max of 1 year at a time
    dates = generate_date_intervals_for_auction_scrape()

    # handle auctions_to_scrape
    # set past_sales variable for use in payload to send in POST request later
    past_sales = 'true'
    if auctions_to_scrape == 'open':
        past_sales = 'false'
        dates = [dates[-1]] if dates else [] # set to just last entry in date range list
    elif auctions_to_scrape == 'one':
        print("\n\nscrape_auctions() called with auctions_to_scrape = 'one'. go implement this.")
        quit()

    for date in dates:
        start_date = date['start_date'].strftime("%Y-%m-%d")
        end_date = date['end_date'].strftime("%Y-%m-%d")
        print(f"\nPulling auctions for affiliate_id {affiliate_id} in date range: {start_date} to {end_date}")

        post_data = {
            "filters[startDate]": start_date
            , "filters[endDate]": end_date
            , "filters[perpage]": 10000
            , "past_sales": past_sales
            , "filters[affiliates]": int(affiliate_id)
        }

        print(f"Attempting to get response from POST request to {post_url}")
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
            print("\n\nRecieved response that wasn't 'success'. Add it to the if/else ladder in scrape_auctions():\n\n")
            print(auction_json)
            quit()

        for auction in auction_data_json:
            # skip if auction is not a real auction
            if auction['item_count'] == '0':
                print(f"Auction {auction['id']} has item_count: 0. Concluding not a real auction and skipping.")
                continue

            auction_url = "https://www.bidrl.com/auction/" + auction['auction_id_slug'] + "/bidgallery/"

            '''# remove any item urls that end with '/i/'
            # track items_removed so that verification function doesn't get tripped up
            # ex: the "I <3 ZACH T-Shirt 2XL" item in this auction:
                # https://www.bidrl.com/auction/high-end-auction-161-johns-rd-unit-a-south-carolina-december-10-143518/bidgallery/perpage_NjA/page_Mg
            items_removed = 0
            for url in item_urls[:]:  # Use a slice copy to iterate over while modifying the original list
                if url.endswith("/i/"):
                    item_urls.remove(url)
                    items_removed += 1
                    print(f"Removed URL ending with '/i/': {url}")'''

            # auction object to hold all of our auction data before we insert it into the sql database
            auction_obj = Auction(
                id=auction['id'],
                url=auction_url,
                items=None,
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

            auctions.append(auction_obj)

    return auctions


# scrapes list of items given an auction_id.
# uses auction's page with /api/getitems. does not gather all item info but works incredibly faster.
# the item info loads all at once, as opposed to sending a request to each item's page
# so we do not get all the information about an item but we do get the list back almost instantly, comparatively (~1s vs ~1m).
# this is useful for getting item ids for full item scraping, and for more efficient grabbing of some item data.
# requires: webdriver object, auction_id of the auction from which we want to gather the item ids,
    # optional indiator to do/skip scraping of images list
# returns: list of item objects
def scrape_items_fast(browser, auction_id, get_images = 'true'):
    response = browser.request('GET', 'https://www.bidrl.com/') # make GET request to get cookies

    post_url = "https://www.bidrl.com/api/getitems"

    # set items per page to 10k to ensure we capture all items in auction
    post_data = {"auction_id": auction_id
                 , "filters[perpage]": 10000
                 , "show_closed": "closed"
                 , "item_type": "itemlist"}
    response = browser.request('POST', post_url, data=post_data)
    response.raise_for_status() # ensure the request was successful

    items = []
    for item_json in response.json()['items']:
        # if get_images is set to true, then get the a list of Image objects for the item
        images = []
        if get_images == 'true':
            for image_json in item_json['images']:
                images.append(Image(**{
                    'item_id': item_json['id']
                    , 'image_url': image_json['image_url']
                    , 'image_height': int(image_json['image_height'])
                    , 'image_width': int(image_json['image_width'])
                }))

        # extract data from json into temp dictionary to create item with later
        temp_item_dict = {'id': item_json['id']
                                , 'auction_id': item_json['auction_id']
                                , 'description': item_json['title']
                                , 'buyer_premium': round(float(item_json['buyer_premium']) * 0.01, 4)
                                , 'current_bid': float(item_json['current_bid'])
                                , 'highbidder_username': item_json['winner']
                                , 'url': item_json['item_url']
                                , 'lot_number': item_json['lot_number']
                                , 'end_time_unix': int(item_json['end_time']) - int(item_json['time_offset'])
                                , 'bid_count': int(item_json['bid_count'])
                                , 'images': images
                            }
        
        # can only see is_favorite key if logged in. check if it exists before attempting to add to dict
        if 'is_favorite' in item_json:
            temp_item_dict['is_favorite'] = int(item_json['is_favorite'])

        # instantiate Item object with info from temp_item_dict and append to list
        items.append(Item(**temp_item_dict))
        
    return items


# requires: webdriver object, auction_id
# returns: list of fully populated item objects for that auction
def scrape_items(browser, auction_id):
    # do fast version of item scrape. we do this just to get the item ids to do full scrape on
    abbrev_items = scrape_items_fast(browser, auction_id)

    print(f"Scraping items from auction with id: {auction_id}.")
    items = []
    for abbrev_item in abbrev_items:
        items.append(get_item_with_ids(browser, abbrev_item.id, auction_id))
    return items


# scrapes list of affiliates from bidrl
# returns: list of Affiliate objects
def scrape_affiliates():
    session = requests.Session() # create a session object to persist cookies
    response = session.get("https://www.bidrl.com/api/affiliates") # make a GET request to get cookies
    affiliates_data = response.json()

    affiliates = []
    if affiliates_data['result'] == 'success':
        for affiliate_data_item in affiliates_data['data'].items():
            affiliate = affiliate_data_item[1]
            affiliate = Affiliate(
                    id = affiliate['id'],
                    logo = affiliate['logo'],
                    do_not_display_tab = int(affiliate['do_not_display_tab']),
                    company_name=affiliate['company_name'],
                    firstname=affiliate['firstname'],
                    lastname = affiliate['lastname'],
                    auc_count = int(affiliate['auc_count'])
                )
            affiliates.append(affiliate)

    return affiliates


# parses the json response returned by bid_on_item() and performs next steps
# just prints result for right now but could do something else in the future maybe, like send a notification, post something to a database, etc.
# bid placement failure error codes I've seen:
    # BID_INSUFFICIENT - "Bidding Error:<br\/>Your bid must be a number equal to or greater than the minimum bid for this item ($1.75)."
    # SAME_BID - "The bid you placed, $1.75, was the same as your current bid so nothing has changed."
    # LOW_BID - "Bidding Error:<br />You cannot bid lower than the current bid."
    # ITEM_CLOSED - "Sorry.  This item is closed."
    # NO_USER - "User must be authenticated before placing bid."
def handle_bid_attempt_response(bid_attempt_response_json):
    try:
        if bid_attempt_response_json["result"] == "success":
            print("Bid placement success!")
        elif bid_attempt_response_json["result"] == "error":
            print(f"Bid placement failed. {bid_attempt_response_json['code']} - {bid_attempt_response_json['message']}")
        return 0
    except:
        print("parse_bid_attempt_response() failed.")
        return 1


# bids x amount of USD on an item via POST request
# requires
    # Item object with id and auction_id populated
    # amount of USD to bid (decimal or int)
    # a webdriver that has logged in to bidrl
# returns json response from bidrl
# to do: need to add protective layer to ensure that not too much money is being bid or that x isn't bid in y amount of time or something
    # ideas:
        # Maximum Bid Limit
            # this is probably a good idea. except the amount I imagine setting as the max is probably an amount that would never
            # get reached by other bidders anyway. like I could imagine a scenario I WOULD want to bid $100 on an item.
        # Daily or Session Bid Total Limit
            # 
        # Confirmation for High Bids
            # no, because I want this to be automatic
        # Rate Limiting
            # possibly! could help with runaway loops during development while I'm testing functions and watching the console
            # I could set cooldown to like 10 secs and I'd see a spam of "cannot bid must wait 10 secs" really fast and could kill it
def bid_on_item(item, amount_to_bid, browser):
    post_url = 'https://www.bidrl.com/api/auctions/' + item.auction_id + '/items/' + item.id + '/bid'

    post_data = {
        "bid": amount_to_bid
        , "accept_terms": 1
    }

    print(f"Attempting to bid ${amount_to_bid} on \"{item.description}\"")

    response = browser.request('POST', post_url, data=post_data) # send the POST request with the session that contains the cookies


    response.raise_for_status() # ensure the request was successful
    handle_bid_attempt_response(response.json())
    
    return response.json()
    

# requires: file path to csv, list of fieldnames to expect in first row
# returns: list of rows read in from csv. each row in list is a dict based on field names
def read_items_from_csv(filename, fieldnames):
    rows = [] # initialize a list to store the rows

    # Read the CSV file
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        # Check if the header matches the expected header
        if reader.fieldnames == fieldnames:
            for row in reader:
                rows.append(row)
        else:
            print("read_items_from_csv(): Header row does not match the expected field names. Exiting program.")
            quit()

    return rows


# establishes connection to sql database
# returns connection object
def init_sql_connection(sql_server_name, sql_database_name, sql_admin_username, sql_admin_password):
    print(f"\nEstablishing connection to server {sql_server_name}, database {sql_database_name}, user {sql_admin_username}")
    # set up connection string
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                        f'SERVER={sql_server_name};'
                        f'DATABASE={sql_database_name};'
                        f'UID={sql_admin_username};'
                        f'PWD={sql_admin_password}')
    return conn

# return sqlite database connection object
# this will create the file if it does not already exist
def init_sqlite_connection():
    print("Initializing sqlite connection")
    conn = sqlite3.connect('local_files/bidrl.db')
    conn.row_factory = sqlite3.Row
    return conn

# returns: 1 if table exists in database and 0 if it does not
def check_if_table_exists(conn, table_name):
    cursor = conn.cursor()
    print(f"Checking if table exists: {table_name}")
    cursor.execute(f'''
        SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name='{table_name}';
    ''')
    result = cursor.fetchone()
    if result:
        if result[0] == 1: return 1
        else: return 0
    else:
        print("error getting result in check_if_table_exists(). Exiting.")
        quit()

def create_table(conn, table_name, table_creation_sql):
    cursor = conn.cursor()
    if check_if_table_exists(conn, table_name) == 0:
        print(f"Does not exist. Creating table: {table_name}.")
        cursor.execute(table_creation_sql)
    else:
        print("Does exist - skipping.")

# inserts an auction object into the auctions table in the sql database
# requires sqlite database connection object and an Auction object
def insert_auction_to_sql_db(conn, auction):
    cur = conn.cursor()
    # Check if auction_id already exists
    cur.execute("SELECT auction_id FROM auctions WHERE auction_id = ?", (auction.id,))
    if cur.fetchone():
        print(f"auction_id {auction.id} already found in database. Skipping insert.")
        return
    else:
        sql = ''' INSERT INTO auctions(auction_id, url, title, item_count, start_datetime, status, affiliate_id, aff_company_name, state_abbreviation, city, zip, address)
                  VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''
        cur.execute(sql, (auction.id, auction.url, auction.title, auction.item_count, auction.start_datetime, auction.status, auction.affiliate_id, auction.aff_company_name, auction.state_abbreviation, auction.city, auction.zip, auction.address))

# inserts an item object into the items table in the sql database
# requires sqlite database connection object and an Item object
def insert_item_to_sql_db(conn, item):
    cursor = conn.cursor()
    # Check if item_id already exists
    cursor.execute("SELECT item_id FROM items WHERE item_id = ?", (item.id,))
    if cursor.fetchone():
        #print(f"item_id {item.id} already found in database. Skipping insert.")
        return
    else:
        sql = ''' INSERT INTO items(item_id, auction_id, description, current_bid, highbidder_username, url, tax_rate, buyer_premium, lot_number, bidding_status, end_time_unix, bid_count, viewed, is_favorite, total_cost, cost_split, max_desired_bid)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''
        cur = conn.cursor()
        cur.execute(sql, (item.id, item.auction_id, item.description, item.current_bid, item.highbidder_username, item.url, item.tax_rate, item.buyer_premium, item.lot_number, item.bidding_status, item.end_time_unix, item.bid_count, item.viewed, item.is_favorite, item.total_cost, item.cost_split, item.max_desired_bid))

# inserts a bid object into the bids table in the sql database
# requires sqlite database connection object and a Bid object
def insert_bid_to_sql_db(conn, bid):
    cur = conn.cursor()
    # Check if bid_id already exists
    cur.execute("SELECT bid_id FROM bids WHERE bid_id = ?", (bid.bid_id,))
    if cur.fetchone():
        #print(f"bid_id {bid.bid_id} already found in database. Skipping insert.")
        return
    else:
        sql = ''' INSERT INTO bids(bid_id, item_id, username, bid, bid_time, time_of_bid, time_of_bid_unix, buyer_number, description)
                  VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?) '''
        cur.execute(sql, (bid.bid_id, bid.item_id, bid.user_name, bid.bid, bid.bid_time, bid.time_of_bid, bid.time_of_bid_unix, bid.buyer_number, bid.description))

# inserts an invoice object into the invoices table in the sql database
# requires sqlite database connection object and an Invoice object
def insert_invoice_to_sql_db(conn, invoice):
    cur = conn.cursor()
    # Check if invoice_id already exists
    cur.execute("SELECT invoice_id FROM invoices WHERE invoice_id = ?", (invoice.id,))
    if cur.fetchone():
        #print(f"invoice_id {invoice.id} already found in database. Skipping insert.")
        return
    else:
        sql = ''' INSERT INTO invoices(invoice_id, date, link, total_cost, expense_input_form_link)
                  VALUES(?, ?, ?, ?, ?) '''
        cur.execute(sql, (invoice.id, invoice.date, invoice.link, invoice.total_cost, invoice.expense_input_form_link))
    

# inserts image URLs associated with an item into the images table in the SQL database
# requires sqlite database connection object and an Item object with a list of image URLs and item_id
def insert_image_to_sql_db(conn, image):
    cursor = conn.cursor()
    sql = ''' INSERT INTO images(item_id, image_url, image_height, image_width)
                  VALUES(?, ?, ?, ?) '''
    cursor.execute(sql, (image.item_id, image.image_url, image.image_height, image.image_width))


# requires a sqlite connection object and an Auction object full of items, each full of bids
# inserts the auction, all items, and all items' bids into the sql database
# rolls back the transaction if any error occurs, so either all the data gets inserted or none of it does
def insert_entire_auction_to_sql_db(conn, auction_obj):
    try:
        conn.execute('BEGIN') # start transaction
        
        #start_time_insert_auction = time.time()
        insert_auction_to_sql_db(conn, auction_obj)
        #print("Auction inserted. Time taken: {:.4f} seconds.".format(time.time() - start_time_insert_auction))

        for item in auction_obj.items:

            #start_time_insert_item = time.time()
            insert_item_to_sql_db(conn, item)
            #print("Item inserted. Time taken: {:.4f} seconds.".format(time.time() - start_time_insert_item))

            #start_time_insert_bids = time.time()
            for bid in item.bids:
                insert_bid_to_sql_db(conn, bid)
            #print("Bids inserted. Time taken: {:.4f} seconds.".format(time.time() - start_time_insert_bids))

            #start_time_insert_images = time.time()
            for image in item.images:
                insert_image_to_sql_db(conn, image)
            #print("Images inserted. Time taken: {:.4f} seconds.".format(time.time() - start_time_insert_images))
        
        conn.commit() # commit the transaction if everything is successful
        return 0
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() # roll back any changes since start of transaction if an error occurs
        return 1


# tear down program gracefully. close webdriver object and exit python scripts
def tear_down(browser):
    print("Tearing down web object and exiting.")
    browser.quit()
    quit()