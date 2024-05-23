import os, sys, getpass, time, re, json, csv
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from config import user_email, user_password, auto_bid_folder_path
from datetime import datetime
import bidrl_functions as bf
from bidrl_classes import Item, Invoice, Auction


bf.ensure_directory_exists('local_files/auto_bid/')

def write_items_to_csv(auctions, filename, fieldnames):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(fieldnames) # write the header

        # write item data
        for auction in auctions:
            for item in auction.items:
                writer.writerow([auction.title, auction.id, item.id, item.description, item.is_favorite, item.url, item.end_time_unix])


 # get an initialized web driver that has logged in to bidrl with credentials stored in config.py
browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')

open_auctions = bf.get_open_auctions_fast(browser)

browser.quit()


filename= auto_bid_folder_path + 'items.csv'
fieldnames = ['auction_title', 'auction_id', 'item_id', 'description', 'is_favorite', 'url', 'end_time_unix']

write_items_to_csv(open_auctions, filename, fieldnames)





