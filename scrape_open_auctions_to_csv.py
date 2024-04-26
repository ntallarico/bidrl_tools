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



open_auctions = get_open_auction_items()
filename='local_files/items.csv'
fieldnames = ['Auction Title', 'Item ID', 'Description', 'Is Favorite', 'URL']

bf.write_items_to_csv(open_auctions, filename, fieldnames)





