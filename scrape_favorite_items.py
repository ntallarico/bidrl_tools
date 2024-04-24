import os, sys, getpass
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from config import user_email, user_password, google_form_link_base
from datetime import datetime
import re
import bidrl_functions as bf


def extract_last_number_from_page_n_of_x(s):
    match = re.search(r'\d+\s*$', s)
    if match:
        return int(match.group().strip())
    return None


# use imported credentials from config.py
user = {'name': user_email, 'pw': user_password}

# open chrome window and set size and position
browser = bf.init_webdriver()

# load and log in to bidrl
bf.login_try_loop(browser, user)

# load favorites page and set max items/page to 60
bf.load_page_favorites(browser, 60)
#bf.load_page_favorites(browser, 60, 'show')
time.sleep(1)

# to do: loop through each page of favorites, and scrape item info

# get max number of pages. we're looking for the "Page 1 of 6" message and want to extract 6.
pager_element = browser.find_element(By.CLASS_NAME, 'pager')
page_n_of_x_text = pager_element.find_element(By.TAG_NAME, 'div').text
max_favs_page_num = extract_last_number_from_page_n_of_x(page_n_of_x_text)

for page_num in range(1, max_favs_page_num + 1): # repeat loop for all ints 1 - max_favs_page_num inclusive
    fav_page_URL_string = 'https://www.bidrl.com/myaccount/myitems/page/' + str(page_num)
    print("going to: " + fav_page_URL_string)
    browser.get(fav_page_URL_string)
    #time.sleep(1)





# to do: export item info to favorite_items.csv



# to do: check "agree to terms" box





# pause program until user input. just for debugging right now
#input()