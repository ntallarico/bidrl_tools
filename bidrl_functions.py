import os, sys, getpass
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from config import user_email, user_password, google_form_link_base
from datetime import datetime
import requests
import json
from bidrl_classes import Item, Invoice, Auction


# open chrome window and set size and position. return web driver object
def init_browser():
    browser = webdriver.Chrome()
    browser.set_window_position(0, 0)
    browser.maximize_window()
    return browser


# attempt to load and log in to bidrl. if that fails, reload the site and try again until this function succeeds
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
        actions.perform()
    except:
        login_try_loop(browser, user)
    return


# go to invoices page, set records per page to 36
def load_page_invoices(browser, records_per_page):
    time.sleep(1) # seems to be needed. tried to fix in various ways and this is one that worked consistently
    browser.get('https://www.bidrl.com/myaccount/invoices')
    time.sleep(1)
    perpage = browser.find_element(By.ID, 'perpage-top')
    actions = ActionChains(browser)
    actions.move_to_element(perpage).click()
    actions.send_keys(str(records_per_page))
    actions.send_keys(Keys.ENTER)
    actions.perform()
    return


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

    

# requires: a web driver, a list of invoice links, a date object indicating the furthest back date of invoice we want to scrape
# returns: a list of Invoice objects (one for each invoice in the link list)
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
            temp_item_dict = {'id': '', 'description': '', 'tax_rate': '', 'amount': '', 'link': ''}

            # get all td elements in row, then iterate through. these are the Lot and Description columns, and where we'll find the item link
            td_elements = tr.find_elements(By.TAG_NAME, 'td')
            if len(td_elements) == 2:
                temp_item_dict['id'] = td_elements[0].text
                temp_item_dict['description'] = td_elements[1].text
                try:
                    temp_item_dict['link'] = td_elements[1].find_element(By.TAG_NAME, 'a').get_property('href')
                except:
                    continue

            # get all th elements in row, then iterate through. these are the Tax Rate and Amount columns
            th_elements = tr.find_elements(By.TAG_NAME, 'th')
            if len(th_elements) == 2:
                temp_item_dict['tax_rate'] = th_elements[0].text
                temp_item_dict['amount'] = th_elements[1].text

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


# calculates total cost of each invoice
# requires: list of Invoice objects with Amount and Tax_Rate attributes populated
# returns: nothing. alters the Invoice objects in the list and the Item objects in the lists of those Invoices
def caculate_total_cost_of_invoices(invoices):
    for invoice in invoices:
        invoice_total_cost = 0
        for item in invoice.items:
            taxed_amount = float(item.tax_rate[-4:]) # last 4 characters of string in Tax Rate field, converted to float
            total_cost_of_item = taxed_amount + float(item.amount)
            invoice_total_cost += total_cost_of_item
            item.total_cost = total_cost_of_item

        invoice.total_cost = invoice_total_cost

    return


# extract item_id and auction_id from the URL string
# returns a dictionary {'item_id': item_id, 'auction_id': auction_id}
def extract_ids_from_url(url):
    parts = url.split('/') # Split the URL by '/'

    item_id_segment = parts[-2] if url.endswith('/') else parts[-1]
    item_id = item_id_segment.split('-')[-1]

    auction_id_segment = parts[-4] if url.endswith('/') else parts[-3]
    auction_id = auction_id_segment.split('-')[-1]

    #print(f"Item ID: {item_id}, Auction ID: {auction_id}")

    return {'item_id': item_id, 'auction_id': auction_id}


# get auctions list
# requires: name of affiliate "company". ex: 'south-carolina'. defaults to sc
# returns: list of Auction objects
def get_open_auctions(affiliate_company_name = 'south-carolina'):
    get_url = "https://www.bidrl.com/api/landingPage/" + affiliate_company_name

    response = requests.get(get_url) # make the GET request

    if response.status_code == 200: # check if the request was successful

        response_json = response.json()
        #print(f"JSON recieved. total auctions: {response_json['total']}")

        # get list of number ids for each auction listed in the JSON
        auctions_num_list = []
        for auction in response_json['auctions']:
            auctions_num_list.append(auction)

        # loop through each auction by number in the json and extract information to an Auction object
        auctions = []
        for auction_num in auctions_num_list:
            auction_json = response_json['auctions'][auction_num]

            auction_url = "https://www.bidrl.com/auction/" + auction_json['auction_id_slug'] + "/bidgallery/perpage_NjA"

            # dictionary to temporarily hold auction details before creating object
            temp_auction_dict = {'id': auction_json['id']
                                 , 'url': auction_url
                                 , 'items': []
                                 , 'title': auction_json['title']
                                 , 'item_count': auction_json['item_count']
                                 , 'start_datetime': auction_json['starts']
                                 , 'status': auction_json['status']}

            # instantiate Autcion item with info from temp_auction_dict and add to list
            auctions.append(Auction(**temp_auction_dict))

        return auctions
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return 0
    

# get item data from api/ItemData
# adapted from first response here:
# https://stackoverflow.com/questions/77120283/selenium-web-scraping-c-sharp-return-views?newreg=2db9cef1711d49e3be9c50d099154a51
def get_item_data(url):
    # extract auction id and item id from url
    extracted_ids = extract_ids_from_url(url)
    item_id = extracted_ids['item_id']
    auction_id = extracted_ids['auction_id']

    session = requests.Session() # Create a session object to persist cookies
    response = session.get(url) # Make a GET request to get the cookies

    # Make a POST request to login or submit data
    post_url = "https://www.bidrl.com/api/ItemData"
    post_data = {
        "item_id": item_id,
        "auction_id": auction_id
    }

    response = session.post(post_url, data=post_data) # Sending the POST request with the session that contains the cookies

    response.raise_for_status() # Ensure the request was successful

    #print(item_data_json)
    #print(response.text)

    return response.json()