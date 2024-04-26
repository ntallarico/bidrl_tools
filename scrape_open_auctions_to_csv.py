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
import csv


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
    return open_auctions


def write_items_to_csv(auctions, filename='local_files/items.csv'):
       with open(filename, mode='w', newline='', encoding='utf-8') as file:
           writer = csv.writer(file)

           writer.writerow(['Auction Title', 'Item ID', 'Description', 'Is Favorite', 'URL']) # write the header

           # write item data
           for auction in auctions:
               for item in auction.items:
                   writer.writerow([auction.title, item.id, item.description, item.is_favorite, item.url])



open_auctions = get_open_auction_items()

write_items_to_csv(open_auctions)



'''
game plan:
1. have this script scrape all open auctions / items to a csv
    - later we can do this with sql or whatever maybe
2. have another script make a copy of that csv, filter it to favorites, and add another column "max price to bid" or whatever
    - this script will also check if that file already exists, and if it does:
        - load in rows from second file, compare it to first, remove rows that aren't present in first
3. at this point - user goes into file created from last script and adds in max desired prices. user will use excel to filter based on is_favorite column
4. auto bid script. this reads in the file from script 2 that is now filled out by the user and wait to bid on items at appropriate time

'''



