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



    


def get_favorites_items():
    # get an initialized web driver that has logged in to bidrl with credentials stored in config.py
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')

    open_auctions = bf.get_open_auctions(browser)

    for auction in open_auctions:
        print(f"\n\nAuction: {auction.title}")
        for item in auction.items:
            if item.is_favorite == '1':
                print('')
                item.display()


get_favorites_items()


# to do: export item info to favorite_items.csv



# to do: check "agree to terms" box





# pause program until user input. just for debugging right now
#input()





