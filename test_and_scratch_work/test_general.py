import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from seleniumrequests import Chrome
import json
import time
from config import user_email, user_password, google_form_link_base
from bidrl_classes import Auction, Item
import bidrl_functions as bf



def test_get_open_auctions():
    open_auctions = bf.get_open_auctions()

    for auction in open_auctions:
        print('')
        auction.display()



def test_get_item_data():
    url = "https://www.bidrl.com/auction/high-end-auction-161-johns-rd-unit-a-south-carolina-april-21-152426/item/metal-beads-item-see-pictures-19718242/"

    item_data = bf.get_item_data(url)

    print(f"ID: {item_data['id']}")
    print(f"Auction ID: {item_data['auction_id']}")
    print(f"Bid Count: {item_data['bid_count']}")
    print(f"Title: {item_data['title']}")



def test_get_auctions_item_urls():
    item_urls = bf.get_auctions_item_urls('https://www.bidrl.com/auction/outdoor-sports-auction-161-johns-rd-unit-a-south-carolina-april-25-152770/bidgallery/')
    for url in item_urls:
        print(url)