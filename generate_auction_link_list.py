'''
This script generates a list of auction links, each set to show the maximum items per page.
'''


import os, sys, getpass
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from config import user_email, user_password, google_form_link_base
from datetime import datetime
import bidrl_functions as bf
from bidrl_classes import Item, Invoice, Auction


def get_auction_urls(affiliate_company_name = 'south-carolina'):
    # get an initialized web driver that has logged in to bidrl with credentials stored in config.py
    #browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')

    # get an initialized web driver. we do not need it to be logged in for scraping auction urls from an affiliate
    browser = bf.init_webdriver('headless')

    get_url = "https://www.bidrl.com/api/landingPage/" + affiliate_company_name

    response = browser.request('GET', get_url) # make the GET request

    if response.status_code != 200: # check if the request was successful
        print(f"Failed to retrieve data: {response.status_code}")
        return 1
    
    response_json = response.json()

    # get list of number ids for each auction listed in the JSON
    auctions_num_list = []
    for auction in response_json['auctions']:
        auctions_num_list.append(auction)

    auction_urls = []
    # loop through each auction by number in the json
    for auction_num in auctions_num_list:
        auction_json = response_json['auctions'][auction_num]
        # create auction url defaulting to show 60 items per page
        auction_url = "https://www.bidrl.com/auction/" + auction_json['auction_id_slug'] + "/bidgallery/perpage_NjA"
        auction_urls.append(auction_url)

    browser.quit()

    return auction_urls


def generate_auction_link_list():
    auction_urls = get_auction_urls()
    print("")
    for url in auction_urls:
        print(url)
    print("")
    
   

if __name__ == "__main__":
    generate_auction_link_list()