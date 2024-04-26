import os, sys, getpass
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from seleniumrequests import Chrome, Firefox
import requests
import time
from config import user_email, user_password, google_form_link_base
from datetime import datetime
import json
from bidrl_classes import Item, Invoice, Auction



def login_try_loop(browser, user):
    browser.get('https://www.bidrl.com/login')
    time.sleep(0.5)
    try:
        userName = browser.find_element(By.NAME, 'username')
        password = browser.find_element(By.NAME, 'password')

        #put all elements with tag name "button" into a list
        button_elements = browser.find_elements(By.TAG_NAME, 'button')
        #find the first element in the button_elements list with text 'LOGIN'
        login_button = next(obj for obj in button_elements if obj.text == 'LOGIN')

        actions = ActionChains(browser)
        actions.move_to_element(userName).send_keys(user['name'])
        actions.send_keys(Keys.TAB).send_keys(user['pw'])
        actions.move_to_element(login_button).click()

        print("Attempting to log in using: " + user['name'])
        actions.perform()
    except:
        login_try_loop(browser, user)
    print("login success")
    return


# initialize webdriver object with Chrome. if not headless, set size and position
def init_webdriver_chrome(headless = ''):
    if headless == 'headless':
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        #chrome_options.add_argument("--log-level=3")
        browser = Chrome(options=chrome_options) # initialize chrome browser webdriver using seleniumrequests library using headless chrome options
        print('Chrome webdriver initialized in headless mode')
    else:
        browser = Chrome() # initialize chrome browser webdriver using seleniumrequests library
        print('Chrome webdriver initialized')
        browser.set_window_position(0, 0)
        browser.maximize_window()
    return browser