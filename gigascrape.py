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
from bidrl_classes import Item, Invoice, Auction
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
def get_all_auctions():
    browser = bf.init_webdriver('headless')

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
            print("\n\nRecieved response that wasn't 'success'. add it to the if/else ladder in get_all_auctions():\n\n")
            print(auction_json)
            quit()


        # for auction in auction_data_json:
        #     print('')
        #     print(auction['id'])
        #     print(auction['title'])
        #     print(auction['affiliate_id'])
        #     print(auction['item_count'])
        #     print(auction['status'])
        #     print(auction['url'])
        #     print(auction['aff_company_name'])
        #     print(auction['state_abbreviation'])
        #     print(auction['city'])
        #     print(auction['zip'])
        #     print(auction['address'])

        auction_url = "https://www.bidrl.com/auction/" + auction_json['auction_id_slug'] + "/bidgallery/"

        print("scaping item urls from: " + auction_url)
        item_urls = bf.get_auction_item_urls(auction_url)
        print(str(len(item_urls)) + " items found")

        print("scraping item info")
        items = bf.get_items(item_urls, browser)

        # dictionary to temporarily hold auction details before creating object
        temp_auction_dict = {'id': auction_json['id']
                                , 'url': auction_url
                                , 'items': items
                                , 'title': auction_json['title']
                                , 'item_count': auction_json['item_count']
                                , 'start_datetime': auction_json['starts']
                                , 'status': auction_json['status']}

        # to do: add fields to Auction class from commented out print statement above
        # to do: create Bid class
        # to do: modify get_items() to return a list of Bids
        # to do: run a check on temp_auction_dict to make sure it has all the data we need
        # to do: then add it to the sql database
    
    browser.quit()

    #return item_json

get_all_auctions()







# conn = bf.init_sql_connection(sql_server_name, sql_database_name, sql_admin_username, sql_admin_password)

# cursor = conn.cursor()



# # Insert Data

# def insert_items(items):
#     for item in items:
#         cursor.execute('''
#         INSERT INTO items (item_id, description, auction_id, end_time_unix, url)
#         VALUES (?, ?, ?, ?, ?)
#         ''', (item['item_id'], item['description'], item['auction_id'], item['end_time_unix'], item['url']))
#     conn.commit()

# # Example usage
# items_data = [{'item_id': 1, 'description': 'Example item', 'auction_id': 101, 'end_time_unix': 1714579800, 'url': 'http://example.com'}]
# insert_items(items_data)






# # Closing the Connection
# conn.close()









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