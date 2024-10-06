'''
This script scrapes everything (affiliate info, acution info, item info, etc) from
all affiliates listed by ID in home_affiliates list in config.py
'''

import os, sys, getpass, time, re, json, csv, requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from seleniumrequests import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import user_email, user_password, home_affiliates#, sql_server_name, sql_database_name, sql_admin_username, sql_admin_password
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from bidrl_classes import Item, Invoice, Auction, Bid
import bidrl_functions as bf
import pyodbc


# run a series of checks on an auction_obj to verify / validate that the object has been
# completely scraped properly. 
# if anything incorrect is found, print indication of what and the relevant object's display function
# some things I found that I needed to account for:
    # https://www.bidrl.com/auction/107248/item/high-speed-remote-control-drift-car-factory-sealed-retail-4999-15080699/
        # has null for a username in bid history
    # https://www.bidrl.com/auction/108065/item/hotwheels-mattel-flying-customs-factory-sealed-15179822/
        # has 103 bids but no highbidder_username
    # https://www.bidrl.com/auction/104502/item/apex-adjustable-massaging-footrest-14830697/
        # has no bid history, but bid_count = 1
    # https://www.bidrl.com/auction/118391/item/glory-season-decorative-throw-blanket-factory-sealed-16188241/
        # has no lot_number
def verify_auction_object_complete(auction_obj, items_removed = 0):
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
            or item.bidding_status == None or item.bidding_status == '' \
            or item.end_time_unix == None or item.end_time_unix == '' \
            or item.bid_count == None or item.bid_count == '':
            print("Element missing from item: ")
            item.display()
            return False
        
        # commented out because apparently this can happen when username is NULL (e.g. https://www.bidrl.com/auction/108065/item/hotwheels-mattel-flying-customs-factory-sealed-15179822/)
        '''if item.highbidder_username == None and item.bid_count != 0:
            print(f"Item {item.url}\n has {item.bid_count} bids but no highbidder_username.")
            item.display()
            return False'''
        
        # return false if bid_count > 0 but the scraped bids list is empty
        # only do this, however, if highbidder_username is null. this was added because
        # some of the items from bidrl have an incorrect bid_count, so we need another element to check
        # to make sure there actually were no bids on the item
        if item.bid_count > 0 and len(item.bids) == 0 and item.highbidder_username != None:
            print(f"Item {item.url}\nhas 0 bids in the bid list" + \
                f", but the bid_count field in the item data is {item.bid_count}")
            item.display_bids()
            return False
        
        # check to make sure the # of bids in the bids list = the bid_count field in the item data
        # this function eliminated because some of the items from bidrl have an incorrect bid_count
        # I cannot figure out why or what the correlation is
        r'''if len(item.bids) != item.bid_count:
            print(f"Item {item.url}\nhas {len(item.bids)} bids in the bid list" + \
                f", but the bid_count field in the item data is {item.bid_count}")
            item.display_bids()
            return False'''
        
        
        # if anything is missing from the auction's item's bids return False
        for bid in item.bids:
            if bid.bid_id == None \
                or bid.item_id == None \
                or bid.bid == None \
                or bid.bid_time == None \
                or bid.time_of_bid == None \
                or bid.time_of_bid_unix == None \
                or bid.description == None:
                print("\nElement missing from bid: ")
                bid.display()
                print("\nItem:")
                item.display()
                return False
            
    # check to make sure the the # of items in the items list = the item_count field in the auction data
    if (len(auction_obj.items) + items_removed) != auction_obj.item_count:
        print(f"Auction {auction_obj.url}\n has {len(auction_obj.items)} items in the items list" + \
              f", but the item_count field in the auction data is {auction_obj.item_count}")
        return False
                
    # if we've made it here, then the auction object is complete and validated. return True
    return True


# gigascrape. this function will scrape all affiliates, auctions, items, bids, and images and inserts them into the database.
# we add an entire scraped aution with full data and all items at once. there will never be a partial auction added.
# plan:
#   1. get list of affiliates.
#   2. for each affiliate, get list of auctions.
#   3. get list of auction_ids with closed status from the sql database and remove any that appear from the list of auctions.
#       - this ensures we are not spending time scraping auction/item data that has already been scraped.
#       - we only pull closed auctions to remove from the list because we want to re-scrape any auctions we previously scraped when live
#   3. for each auction, get list of items.
#   4. every time we scrape an auction and its items, verify the auction object is complete, then add to the database.
def gigascrape():
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
    conn = bf.init_sqlite_connection()
    cursor = conn.cursor()

    # attempt to scrape and insert all affiliate information to database
    bf.scrape_and_insert_all_affiliates_to_sql_db(conn)
    conn.commit()

    # get all closed auction_ids from sql database so we can skip scraping completed auctions that have already been scraped
    cursor.execute("SELECT auction_id FROM auctions WHERE status = 'closed'")
    auctions_in_db = cursor.fetchall()
    # extract auction_id from each row and store in a list
    auction_ids_in_db = [auction['auction_id'] for auction in auctions_in_db]

    affiliates = bf.scrape_affiliates()


    # filter affiliates to include only those in the home_affiliates list
    affiliates = [affiliate for affiliate in affiliates if affiliate.id in home_affiliates]
    # sort the list of affiliates to match the order of affiliate IDs in home_affiliates
    affiliates = sorted(affiliates, key=lambda x: home_affiliates.index(x.id) if x.id in home_affiliates else len(home_affiliates))
    # print affiliates list
    print("\nBased on IDs in home_affiliates list, auctions will be scraped from:")
    for affiliate in affiliates:
        print(f"{affiliate.company_name}")

    


    try:
        for affiliate in affiliates:
            print("\nScraping auctions for affiliate: " + affiliate.company_name)
            auctions = bf.scrape_auctions(browser, affiliate.id)

            # keep only auctions that are not already in the database
            auctions_already_scraped = 0
            # we do auctions[:] to iterate through a copy, so we can do auctions.remove() while in the loop
            for auction in auctions[:]: 
                if auction.id in auction_ids_in_db:
                    auctions.remove(auction)
                    auctions_already_scraped += 1
            print(f"\n{auctions_already_scraped} auctions already scraped.")

            auctions_scraped_this_run = 0
            for auction in auctions:
                print('')
                print(f"{affiliate.company_name} auctions complete: {auctions_already_scraped + auctions_scraped_this_run}."
                      f" Remaining: {len(auctions) - auctions_scraped_this_run}")
                start_time_scrape_auction_items = time.time()
                auction.items = bf.scrape_items(browser, auction.id)
                print(f"Auction items scraped: {len(auction.items)}" + ". Time taken: {:.4f} seconds".format(time.time() - start_time_scrape_auction_items))

                if verify_auction_object_complete(auction) == False:
                    print("Auction did not pass verification! Not adding to sql database. Exiting program.")
                    quit()
                else:
                    print("Auction object passed verification. Attempting to add to sql database.")
                    start_time_insert_auction_to_sql = time.time()
                    if bf.insert_entire_auction_to_sql_db(conn, auction) == 0:
                        print("Successfully added to database. Time taken: {:.4f} seconds.".format(time.time() - start_time_insert_auction_to_sql))
                        auctions_scraped_this_run += 1
                    else:
                        print("Failed to add to database. Exiting.")
                        quit()
            
            print(f"\nCompleted full scrape of affiliate {affiliate.company_name}!")

        print("\ngigacrape complete! everything is now yours. have fun :)")
        browser.quit()
    finally:
        browser.quit()


if __name__ == "__main__":
    gigascrape()

