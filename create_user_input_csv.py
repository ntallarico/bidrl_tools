import os, sys, getpass, time, re, json, csv
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from config import user_email, user_password, google_form_link_base
from datetime import datetime
import bidrl_functions as bf
from bidrl_classes import Item, Invoice, Auction



fieldnames_to_read = ['Auction_Title', 'Item_ID', 'Description', 'Is_Favorite', 'URL']
filename_to_read = 'local_files/items.csv'


read_rows = bf.read_items_from_csv(filename_to_read, fieldnames_to_read)

# rows list for user interface file. list of dicts
rows_to_write = []

for row in read_rows:
    if row['Is_Favorite'] == '1':
        temp_row_dict = {'Auction_Title': row['Auction_Title'], 'Item_ID': row['Item_ID'], 'Description': row['Description'], 'Is_Favorite': row['Is_Favorite'], 'URL': row['URL']}
        rows_to_write.append(temp_row_dict)

filename_to_write = 'local_files/favorite_items_to_input_max_bid.csv'


# check if the file already exists and ask for user input to confirm overwriting it if it does
if os.path.exists(filename_to_write):
    user_input = input(f"The file '{filename_to_write}' already exists, possibly with your max bids in it. Do you want to overwrite it? (y/n): ")
    
    if user_input.lower() != 'y':
        print("File will not be overwritten. Exiting.")
        quit()
else:
    print(f"Creating '{filename_to_write}'.")


with open(filename_to_write, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    writer.writerow(['Auction_Title', 'Item_ID', 'Description', 'Is_Favorite', 'URL', 'Max_Desired_Bid']) # write the header, adding "Max Desired Bid"

    # write item data
    for row in rows_to_write:
        writer.writerow([row['Auction_Title'], row['Item_ID'], row['Description'], row['Is_Favorite'], row['URL'], ''])




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