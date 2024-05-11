import os, sys, getpass, time, re, json, csv, requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from seleniumrequests import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from bidrl_classes import Item, Invoice, Auction, Bid
from bs4 import BeautifulSoup
import pyodbc
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
                        'id': '',
                        'date': '',
                        'link': invoice_url,
                        'items': [],
                        'total_cost': ''
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
                    #tax_rate = cells[2].get_text(strip=True).split('-')[0].strip()
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
                            'current_bid': amount,
                            'url': item_url
                        }))
                    #invoice.items[len(items)-1].display() # call display function for most recent item added
                    
                except Exception as e:
                    print(f"Error processing row: {e}")
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
def caculate_total_cost_of_invoices(invoices):
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

    #print(f"Item ID: {item_id}, Auction ID: {auction_id}")

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


'''
- get list of item urls from an auction
- requires URL in this format:
https://www.bidrl.com/auction/outdoor-sports-auction-161-johns-rd-unit-a-south-carolina-april-25-152770/bidgallery/
- returns: list of urls, one for each item in the auction provided
'''
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


# requires instantiated webdriver, item_id, auction_id, and optionally an indication to also/not scrape bids
# returns an Item object
def get_item_with_ids(browser, item_id, auction_id, get_bid_history = 'true'):
    response = browser.request('GET', 'https://www.bidrl.com/') # make GET request to get cookies

    # submit requests to API and get JSON response
    post_url = "https://www.bidrl.com/api/ItemData"
    post_data = {
        "item_id": item_id
        , "auction_id": auction_id
        , "show_closed": "closed"
    }
    response = browser.request('POST', post_url, data=post_data) # send the POST request with the session that contains the cookies
    response.raise_for_status() # ensure the request was successful
    item_json = response.json()

    # if get_bid_history is set to true, then get the bid history for the item
    bids = []
    if get_bid_history == 'true':
        for bid_json in item_json['bid_history']:
            bids.append(Bid(**{
                'bid_id': bid_json['id']
                , 'item_id': item_json['id']
                , 'user_name': bid_json['user_name']
                , 'bid': bid_json['bid']
                , 'bid_time': bid_json['bid_time']
                , 'time_of_bid': bid_json['time_of_bid']
                , 'time_of_bid_unix': bid_json['time_of_bid_unix']
                , 'buyer_number': bid_json['buyer_number']
                , 'description': bid_json['description']
            }))
            #bids[len(bids)-1].display()

    # extract data from json into temp dictionary to create item with later
    temp_item_dict = {'id': item_json['id']
                            , 'auction_id': item_json['auction_id']
                            , 'description': item_json['title']
                            , 'tax_rate': str(round(float(item_json['tax_rate']) * 0.01, 4))
                            , 'buyer_premium': str(round(float(item_json['buyer_premium']) * 0.01, 4))
                            , 'current_bid': item_json['current_bid']
                            , 'highbidder_username': item_json['highbidder_username']
                            , 'url': item_json['url']
                            , 'lot_number': item_json['lot_number']
                            , 'bidding_status': item_json['bidding_status']
                            , 'end_time_unix': int(item_json['end_time_unix']) - int(item_json['time_offset'])
                            , 'bids': bids
                            , 'bid_count': item_json['bid_count']}
    
    # can only see is_favorite key if logged in. check if it exists before attempting to add to dict
    if 'is_favorite' in item_json:
        temp_item_dict['is_favorite'] = item_json['is_favorite']

    # instantiate Item object with info from temp_auction_dict, print message, and return item object
    item_obj = Item(**temp_item_dict)
    #print(f"get_item_with_ids() scraped: {item_obj.description} (with {len(bids)} bids)")
    return item_obj


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


# get auctions list
# requires:
    # name of affiliate "company". ex: 'south-carolina'. defaults to sc
    # webdriver object. if webdriver object has been logged in as a user, then the attribute is_favorite will be filled in for items
# returns: list of Auction objects
def get_open_auctions(browser, affiliate_company_name = 'south-carolina'):
    get_url = "https://www.bidrl.com/api/landingPage/" + affiliate_company_name

    response = browser.request('GET', get_url) # make the GET request

    if response.status_code == 200: # check if the request was successful

        response_json = response.json()
        #print(f"JSON recieved. total auctions: {response_json['total']}")

        # get list of number ids for each auction listed in the JSON
        auctions_num_list = []
        for auction in response_json['auctions']:
            auctions_num_list.append(auction)

        #auctions_num_list = auctions_num_list[0] # FOR DEBUGGING. causes function to only scrape first auction

        # loop through each auction by number in the json and extract information to an Auction object
        auctions = []
        for auction_num in auctions_num_list:
            auction_json = response_json['auctions'][auction_num]

            auction_url = "https://www.bidrl.com/auction/" + auction_json['auction_id_slug'] + "/bidgallery/"

            print("scaping item urls from: " + auction_url)
            item_urls = get_auction_item_urls(auction_url)
            print(str(len(item_urls)) + " items found")

            print("scraping item info")
            items = get_items(item_urls, browser)

            # dictionary to temporarily hold auction details before creating object
            temp_auction_dict = {'id': auction_json['id']
                                 , 'url': auction_url
                                 , 'items': items
                                 , 'title': auction_json['title']
                                 , 'item_count': auction_json['item_count']
                                 , 'start_datetime': auction_json['starts']
                                 , 'status': auction_json['status']}
            
            # instantiate Autcion object with info from temp_auction_dict and add to list
            auctions.append(Auction(**temp_auction_dict))

        return auctions
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return 1
    

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