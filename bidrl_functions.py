import os, sys, getpass
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from config import user_email, user_password, google_form_link_base
from datetime import datetime
from bidrl_classes import Item, Invoice


# open chrome window and set size and position. return web driver object
def init_browser():
    browser = webdriver.Chrome()
    browser.set_window_position(0, 0)
    browser.maximize_window()
    return browser


# attempt to load and log in to bidrl. if that fails, reload the site and try again until this function succeeds
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
        actions.perform()
    except:
        login_try_loop(browser, user)
    return


# go to invoices page, set records per page to 36
def load_page_invoices(browser, records_per_page):
    time.sleep(1)
    browser.get('https://www.bidrl.com/myaccount/invoices')
    perpage = browser.find_element(By.ID, 'perpage-top')
    actions = ActionChains(browser)
    actions.move_to_element(perpage).click()
    actions.send_keys(str(records_per_page))
    actions.send_keys(Keys.ENTER)
    actions.perform()
    return


# go to favorites page, set records per page to 36
def load_page_favorites(browser, records_per_page):
    time.sleep(1)
    browser.get('https://www.bidrl.com/myaccount/myitems')
    perpage = browser.find_element(By.ID, 'perpage-top')
    actions = ActionChains(browser)
    actions.move_to_element(perpage).click()
    actions.send_keys(str(records_per_page))
    actions.send_keys(Keys.ENTER)
    actions.perform()
    return

    