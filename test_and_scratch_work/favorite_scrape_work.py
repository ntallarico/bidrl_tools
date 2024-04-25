import sys
import os
# tell this file that the root directory is one folder level up so that it can read our files like config, bidrl_classes, etc
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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



# to do: scrape favorites
# in order to do this, I will do one of 3 things:
# 1. traditional selenium scrape, navigating through the favorites pages
# 2. use requests library and api to scrape all items from all open auctions and check if any of them have is_favorite = 1
# 3. use requests library to scrape html response on favorites page and parse out the items
# the first seems inideal and I'd like to try moving away from this method if possible
# the latter two would require getting a logged in session or something somehow
# the last seems like it could be potentially inideal as the html could change slightly
# I would rank these options in order of preference: 2, 3, 1
# I will try them in this order




'''
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
'''





'''
new aproach. here, we:
1. get a logged in session
2. scrape the page with a get response
3. find the items json in the response text
4. parse the text into a json object
5. (not implemented) extract item info from each item in the json and use it to populate item objects, appending them to a list
6. (not implemented) loop through all remaining favorites pages and scrape items from them too
'''
'''
# get an initialized web driver that has logged in to bidrl with credentials stored in config.py
browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')

response = browser.request('GET', 'https://www.bidrl.com/myaccount/myitems/hide_closed/1')

# Regular expression to extract the JSON-like object
pattern = r"myAccount\.factory\('myAccountData', function\(\){\s*var data = {};\s*data\.items = (\[.*?\]);"
match = re.search(pattern, response.text, re.DOTALL)

if match:
    # Convert the matched string to a valid JSON object
    items_json = match.group(1)
    items_data = json.loads(items_json)
    print(items_data)
else:
    print("No data found")


# to do: parse the json into a list of item objects

# to do: loop through the pages and get items from them too
# response = browser.request('GET', 'https://www.bidrl.com/myaccount/myitems/page/2')'''




'''
in this approach, we scrape all items from all open auctions as a logged in user and then filter down to just items where is_favorite == 1

'''

'''
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

'''