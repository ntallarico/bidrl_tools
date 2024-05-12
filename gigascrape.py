import os, sys, getpass, time, re, json, csv, requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from seleniumrequests import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import user_email, user_password#, sql_server_name, sql_database_name, sql_admin_username, sql_admin_password
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from bidrl_classes import Item, Invoice, Auction, Bid
import bidrl_functions as bf
import pyodbc



# generates a list of dicts with start_date and end_date to use as intervals for auction scraping
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


# run a series of checks on an auction_obj to verify / validate that the object has been
# completely scraped properly. 
# if anything incorrect is found, print indication of what and the relevant object's display function
def verify_auction_object_complete(auction_obj):
    # if anything is missing from the auction return False
    if auction_obj.id == None \
        or auction_obj.url == None \
        or auction_obj.items == None \
        or auction_obj.title == None \
        or auction_obj.item_count == None \
        or auction_obj.start_datetime == None \
        or auction_obj.status == None \
        or auction_obj.affiliate_id == None \
        or auction_obj.aff_company_name == None \
        or auction_obj.state_abbreviation == None \
        or auction_obj.city == None \
        or auction_obj.zip == None \
        or auction_obj.address == None:
        print("Element missing from auction: ")
        bid.auction_obj()
        return False
    
    # if anything is missing from the auction's items return False
    for item in auction_obj.items:
        if item.id == None or item.id == '' \
            or item.auction_id == None or item.auction_id == '' \
            or item.description == None or item.description == '' \
            or item.tax_rate == None or item.tax_rate == '' \
            or item.buyer_premium == None or item.buyer_premium == '' \
            or item.current_bid == None or item.current_bid == '' \
            or item.url == None or item.url == '' \
            or item.lot_number == None or item.lot_number == '' \
            or item.bidding_status == None or item.bidding_status == '' \
            or item.end_time_unix == None or item.end_time_unix == '' \
            or item.bid_count == None or item.bid_count == '':
            print("Element missing from item: ")
            item.display()
            return False
        
        if item.highbidder_username == None and item.bid_count != str(0):
            print(f"Item {item.url}\n has {item.bid_count} bids but no highbidder_username.")
            item.display()
            return False
        
        # check to make sure that the bids list is not empty if bid_count > 0
        if int(item.bid_count) > 0 and len(item.bids) == 0:
            print(f"Item {item.url}\nhas 0 bids in the bid list" + \
                f", but the bid_count field in the item data is {item.bid_count}")
            item.display_bids()
            return False
        
        # check to make sure the # of bids in the bids list = the bid_count field in the item data
        # this function eliminated because some of the items from bidrl have an incorrect bid_count
        # I cannot figure out why or what the correlation is
        r'''if str(len(item.bids)) != item.bid_count:
            print(f"Item {item.url}\nhas {len(item.bids)} bids in the bid list" + \
                f", but the bid_count field in the item data is {item.bid_count}")
            item.display_bids()
            return False'''
        
        
        # if anything is missing from the auction's item's bids return False
        for bid in item.bids:
            if bid.bid_id == None \
                or bid.item_id == None \
                or bid.user_name == None \
                or bid.bid == None \
                or bid.bid_time == None \
                or bid.time_of_bid == None \
                or bid.time_of_bid_unix == None \
                or bid.description == None:
                print("Element missing from bid: ")
                bid.display()
                return False
            
    # check to make sure the the # of items in the items list = the item_count field in the auction data
    if str(len(auction_obj.items)) != auction_obj.item_count:
        print(f"Auction {auction_obj.url}\n has {len(auction_obj.items)} items in the items list" + \
              f", but the item_count field in the auction data is {auction_obj.item_count}")
        return False
                
    # if we've made it here, then the auction object is complete and validated. return True
    return True


# we'll add an entire scraped aution with its full data and all items at once.
    # so there will never be a partial auction added. instead of adding all auctions, then items, then history
    # we'll go one auction at a time. Therefore, since its quick to get a list of auctions from the API for
    # an affiliate, then we can just get a list of auction_ids from the sql and remove that from our list from
    # the api. then just exclusively scrape the remaining list.
    # plan:
    #   1. only insert to the sql once we have absolutely all the data for an auction.
    #   2. get list of auctions from the api
    #   3. get list of auction_ids from the sql (this is the list of auctions that we've already scraped)
    #   4. remove auction_ids from the api list that are in the sql list
    #   5. loop through the remaining auctions in the api list, then get all the data for that auction
    #   6. insert the data for that auction into the sql
def gigascrape():
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
    conn = bf.init_sqlite_connection()
    cursor = conn.cursor()

    # send browser to bidrl.com. this gets us the cookies we need to send the POST requests properly next
    browser.get('https://www.bidrl.com')

    post_url = "https://www.bidrl.com/api/auctions"

    # get list of date intervals to pull auctions from
    # can only pull a max of 1 year at a time
    dates = generate_date_intervals_for_auction_scrape()
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
            auction_data_json = auction_json['data'][2:]
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

            auction_url = "https://www.bidrl.com/auction/" + auction['auction_id_slug'] + "/bidgallery/"

            print("scaping item urls from: " + auction_url)
            item_urls = bf.get_auction_item_urls(auction_url)
            print(str(len(item_urls)) + " items found")

            print("scraping item info")
            items = bf.get_items(item_urls, browser)


            # auction object to hold all of our auction data before we insert it into the sql database
            auction_obj = Auction(
                id=auction['id'],
                url=auction_url,
                items=items,
                title=auction['title'],
                item_count=auction['item_count'],
                start_datetime=auction['starts'],
                status=auction['status'],
                affiliate_id=auction['affiliate_id'],
                aff_company_name=auction['aff_company_name'],
                state_abbreviation=auction['state_abbreviation'],
                city=auction['city'],
                zip=auction['zip'],
                address=auction['address']
            )

            if verify_auction_object_complete(auction_obj) == False:
                print("Auction did not complete! Not adding to sql database. Exiting program.")
                quit()
            else:
                print("Auction object is complete! Adding to sql database.")
                bf.insert_entire_auction_to_sql_db(conn, auction_obj) # add auction to sql database
                print("Completed attempt to add to database.")
    
    browser.quit()


gigascrape()









'''
questions I'd like to answer in reporting once I have full database:
- what bidding strategy / timing works best? bidding one single time at 2mins out? 10 seconds out? is there a difference on average at all?
    - need to analyze full population's bid history

'''





'''
surveillance project

- I'll need a list of all auction ids
    - brute force?? need to be careful not to DDOS lol
- then from each auction id I'll need a list of all item ids in those auctions
    - possibly an API call for this? like a GetItems or something
- then I'll just need to loop through all auctions, then all items under each auction, then I'll have all the data! easy as that
'''