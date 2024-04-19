import os, sys, getpass
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from config import user_email, user_password, google_form_link_base
from datetime import datetime
import bidrl_functions as bf




# init window and log in to bidrl

# use imported credentials from config.py
user = {'name': user_email, 'pw': user_password}

# open chrome window and set size and position
browser = bf.init_browser()

# load and log in to bidrl
bf.login_try_loop(browser, user)




# to do: go to favorite items list, set to max items/page, loop through each page and, and scrape item info

# load favorites page and set max items/page to 60
bf.load_page_favorites(browser, 60)



# to do: export item info to favorite_items.csv



# to do: check "agree to terms" box





# pause program until user input. just for debugging right now
input()