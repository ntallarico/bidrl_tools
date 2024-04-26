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







fieldnames = ['Auction Title', 'Item ID', 'Description', 'Is Favorite', 'URL']
filename = 'local_files/items.csv'

rows = bf.read_items_from_csv(filename, fieldnames)

# display the read rows
for row in rows:
    if row['Is Favorite'] == '1':
        print(row)





'''
game plan:
1. have this script scrape all open auctions / items to a csv. scrape_open_auctions_to_csv.py
    - later we can do this with sql or whatever maybe
2. have another script make a copy of that csv, filter it to favorites, and add another column "max price to bid" or whatever
    - this script will also check if that file already exists, and if it does:
        - load in rows from second file, compare it to first, remove rows that aren't present in first
3. at this point - user goes into file created from last script and adds in max desired prices. user will use excel to filter based on is_favorite column
4. auto bid script. this reads in the file from script 2 that is now filled out by the user and wait to bid on items at appropriate time

'''