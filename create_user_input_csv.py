import os, sys, getpass, time, re, json, csv
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from config import user_email, user_password, google_form_link_base
from datetime import datetime
import bidrl_functions as bf
from bidrl_classes import Item, Invoice, Auction


bf.ensure_directory_exists('local_files/auto_bid/')


fieldnames_to_read = ['auction_title', 'auction_id', 'item_id', 'description', 'is_favorite', 'url', 'end_time_unix']
filename_to_read = 'local_files/auto_bid/items.csv'


read_rows = bf.read_items_from_csv(filename_to_read, fieldnames_to_read)

# rows list for user input file. list of dicts
rows_to_write = []

for row in read_rows:
    if row['is_favorite'] == '1':
        temp_row_dict = {'auction_title': row['auction_title'], 'auction_id': row['auction_id'], 'item_id': row['item_id'], 'description': row['description'], 'is_favorite': row['is_favorite'], 'url': row['url'], 'end_time_unix': row['end_time_unix']}
        rows_to_write.append(temp_row_dict)

filename_to_write = 'local_files/auto_bid/favorite_items_to_input_max_bid.csv'


# check if the file already exists and ask for user input to confirm overwriting it if it does
if os.path.exists(filename_to_write):
    user_input = input(f"The file '{filename_to_write}' already exists, possibly with your max bids in it. Do you want to overwrite it? (y/n): ")
    
    if user_input.lower() != 'y':
        print("File will not be overwritten. Exiting.")
        quit()
    else:
        print(f"Overwriting '{filename_to_write}'.")
else:
    print(f"Creating '{filename_to_write}'.")


with open(filename_to_write, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    writer.writerow(['end_time_unix', 'auction_id', 'item_id', 'item_bid_group_id', 'description', 'max_desired_bid', 'url']) # write the header, adding "Max Desired Bid"

    # write item data
    for row in rows_to_write:
        writer.writerow([row['end_time_unix'], row['auction_id'], row['item_id'], row['item_id'], row['description'], '', row['url']])

