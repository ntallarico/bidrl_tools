import os, sys, getpass
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from config import user_email, user_password, google_form_link_base
from datetime import datetime
import re
import json
import bidrl_functions as bf
from bidrl_classes import Item, Invoice, Auction



    


def get_open_auction_items():
    # get an initialized web driver that has logged in to bidrl with credentials stored in config.py
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')

    open_auctions = bf.get_open_auctions(browser)

    for auction in open_auctions:
        print(f"\n\nAuction: {auction.title}")
        for item in auction.items:
            if item.is_favorite == '1':
                print(f"Item (Favorite): {item.description}")
            else:
                print(f"Item: {item.description}")
    
    browser.quit()


get_open_auction_items()


'''
game plan:
1. have this script scrape all open auctions / items to a csv
    - later we can do this with sql or whatever maybe
2. have another script make a copy of that csv and add another column "max price to bid" or whatever
    - this script will also check if that file already exists
3. at this point - user goes into file created from last script and adds in max desired prices. user will use excel to filter based on is_favorite column
4. auto bid script. this reads in the file from script 2 that is now filled out by the user and wait to bid on items at appropriate time

'''



