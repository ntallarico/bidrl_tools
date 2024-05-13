import os, sys, getpass, time, re, json, csv
# tell this file that the root directory is one folder level up so that it can read our files like config, bidrl_classes, etc
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from seleniumrequests import Chrome, Firefox
from config import user_email, user_password, google_form_link_base
from bidrl_classes import Auction, Item, Invoice
import bidrl_functions as bf
from bs4 import BeautifulSoup



def test_get_open_auctions():
    # get an initialized web driver that has logged in to bidrl with credentials stored in config.py
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
    open_auctions = bf.get_open_auctions(browser)

    for auction in open_auctions:
        print('')
        auction.display()

    browser.quit()




def test_get_item_data():
    url = "https://www.bidrl.com/auction/high-end-auction-161-johns-rd-unit-a-south-carolina-april-21-152426/item/metal-beads-item-see-pictures-19718242/"

    item_data = bf.get_item_data(url)

    print(f"ID: {item_data['id']}")
    print(f"Auction ID: {item_data['auction_id']}")
    print(f"Bid Count: {item_data['bid_count']}")
    print(f"Title: {item_data['title']}")



def test_get_auctions_item_urls():
    item_urls = bf.get_auctions_item_urls('https://www.bidrl.com/auction/outdoor-sports-auction-161-johns-rd-unit-a-south-carolina-april-25-152770/bidgallery/')
    for url in item_urls:
        print(url)



def test_bid_on_item():
    item_urls = ['https://www.bidrl.com/auction/kitchen-goods-auction-161-johns-rd-unit-a-south-carolina-april-25-152706/item/bath-loofah-shower-sponges-6-pack-factory-sealed-19755497/']
    amount_to_bid = 1.75

    # get an initialized web driver that has logged in to bidrl with credentials stored in config.py
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
    item_obj_list = bf.get_items(item_urls, browser)
    bf.bid_on_item(item_obj_list[0], amount_to_bid, browser)

    browser.quit()

#test_bid_on_item()


# get an initialized web driver that has logged in to bidrl with credentials stored in config.py

def test_get_invoices():
    # get an initialized web driver that has logged in to bidrl with credentials stored in config.py
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')

    invoices = bf.get_invoices(browser)
    for invoice in invoices:
        invoice.display()

#test_get_invoices()



def test_parse_invoice_page():
    # get an initialized web driver that has logged in to bidrl with credentials stored in config.py
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')

    invoice_url = 'https://www.bidrl.com/myaccount/invoice/invid/3027107'
    invoice = bf.parse_invoice_page(browser, invoice_url)
    #invoice.display()

    print("\n\n")

    invoice_url = 'https://www.bidrl.com/myaccount/invoice/invid/3262831' # previously broken one. bug fixed
    invoice = bf.parse_invoice_page(browser, invoice_url)
    #invoice.display()

#test_parse_invoice_page()


def test_get_item_with_ids():
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
    item_obj = bf.get_item_with_ids(browser, '14838053', '104503')
    item_obj.display()
    item_obj.display_bids()

#test_get_item_with_ids()

def test_insert_auction_to_sql_db():
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
    item_obj = bf.get_item_with_ids(browser, '14838053', '104503')
    conn = bf.init_sqlite_connection()
    bf.insert_auction_to_sql_db(conn, item_obj)
    conn.commit()

#test_insert_auction_to_sql_db()


def test_insert_auction_to_sql_db():
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
    auction_obj = bf.get_open_auctions(browser, debug = 'true')[0]
    conn = bf.init_sqlite_connection()
    cursor = conn.cursor()
    bf.insert_auction_to_sql_db(conn, auction_obj)
    conn.commit()
    
    cursor.execute("SELECT * FROM auctions")
    auctions = cursor.fetchall()
    for auction in auctions:
        print(auction)

#test_insert_auction_to_sql_db()


def test_insert_item_to_sql_db():
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
    item_obj = bf.get_item_with_ids(browser, '14838053', '104503')
    conn = bf.init_sqlite_connection()
    cursor = conn.cursor()
    bf.insert_item_to_sql_db(conn, item_obj)

    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    for item in items:
        print(item)

#test_insert_item_to_sql_db()


def test_insert_bid_to_sql_db():
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
    item_obj = bf.get_item_with_ids(browser, '14838053', '104503')
    conn = bf.init_sqlite_connection()
    cursor = conn.cursor()
    bf.insert_bid_to_sql_db(conn, item_obj.bids[1])

    cursor.execute("SELECT * FROM bids")
    bids = cursor.fetchall()
    for bid in bids:
        print(bid)

#test_insert_bid_to_sql_db()


def test_get_auction():
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
    auction_obj = bf.get_open_auctions(browser, debug = 'true')[0]
    auction_obj.display()


#test_get_auction()




def test_insert_entire_auction_to_sql_db():
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
    auction_obj = bf.get_open_auctions(browser, debug = 'true')[0]
    conn = bf.init_sqlite_connection()
    cursor = conn.cursor()
    bf.insert_entire_auction_to_sql_db(conn, auction_obj)
    conn.commit()
    
    print("\n\n\nAuctions:")
    cursor.execute("SELECT * FROM auctions")
    auctions = cursor.fetchall()
    for auction in auctions:
        print(auction['auction_id'])

    # print("\n\n\nItems:")
    # cursor.execute("SELECT * FROM items")
    # items = cursor.fetchall()
    # for item in items:
    #     print(item)

    # print("\n\n\nBids:")
    # cursor.execute("SELECT * FROM bids")
    # bids = cursor.fetchall()
    # for bid in bids:
    #     print(bid)

#test_insert_entire_auction_to_sql_db()


def test_itemdata_api():
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')

    response = browser.request('GET', 'https://www.bidrl.com/') # make GET request to get cookies

    # submit requests to API and get JSON response
    post_url = "https://www.bidrl.com/api/ItemData"
    post_data = {
        "item_id": '18461004'
        , "auction_id": '143518'
        , "show_closed": "closed"
    }
    response = browser.request('POST', post_url, data=post_data) # send the POST request with the session that contains the cookies
    try:
        response.raise_for_status() # ensure the request was successful
    except requests.exceptions.HTTPError as err:
        print(f"Error in get_item_with_ids(): {err}")
        print(f"post_url: {post_url}")
        print(f"post_data: {post_data}")
        quit()
    item_json = response.json()

    print(item_json)


#test_itemdata_api()

def test_scrape_auctions():
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
    auctions = bf.scrape_auctions(browser)
    for auction in auctions:
        #auction.display()
        print(auction.id)
    browser.quit()

#test_scrape_auctions()

def test_scrape_item_id_list_from_auction():
    item_ids = bf.scrape_item_id_list_from_auction('114048')
    for item_id in item_ids:
        print(item_id)

#test_scrape_item_id_list_from_auction()

def test_scrape_items():
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
    items = bf.scrape_items(browser, '114048')
    for item in items:
        item.display()
    browser.quit()

#test_scrape_items()

def test_scrape_affiliates():
    affiliates = bf.scrape_affiliates()
    for affiliate in affiliates:
        affiliate.display()

#test_scrape_affiliates()






'''
other api reference i've seen to explore:
- https://www.bidrl.com/api/types/auctions
- https://www.bidrl.com/api/types/errors
- https://www.bidrl.com/api/types/items
- https://www.bidrl.com/api/relations/auction_item
- https://www.bidrl.com/api/auctions
    - https://www.bidrl.com/api/auctions/114048
    - used by https://www.bidrl.com/pastauctions/
    - seems to gather all past auctions (possibly up to a certain point), which is incredible
- https://www.bidrl.com/api/auctionfields
- https://www.bidrl.com/api/initdata
- https://www.bidrl.com/api/affiliatesforhomepage
- https://www.bidrl.com/api/getsession
- 
'''




















'''
bidding notes

https://www.bidrl.com/auction/personal-care-health-beauty-auction-161-johns-rd-unit-a-south-carolina-april-24-152767/item/one-two-lash-magnetic-lashes-factory-sealed-19776588/


when submitting a bid on the above url with a bid of $1.50, and accepting the terms at the same time, I got the following in Network inspect element:

bid
    https://www.bidrl.com/api/auctions/152767/items/19776588/bid
    POST

    payload:
        bid: 1.5
        accept_terms: 1
        buyer_number: 
        shipping_method: pickup

auctionterms
    https://www.bidrl.com/api/auctionterms
    POST

    payload:
        id: 152767


I then submitted a bid after already having accepted the terms on an earlier item, and I got the same exact result

I tried to submit a bid without accepting the terms and got blocked on client side. no network activity present

I'm wondering if I can just submit the bid straight up with "accept_terms: 1" in the payload, or if I need to POST auctionterms first

update 4.25.24:
this turned out to be true! no auctionterms POST needed. only need to POST bid with "bid" and "accept_terms" pieces in payload

'''


