import os, sys, getpass
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from config import user_email, user_password  # Import from config.py

# Use imported credentials
user = {'name': user_email, 'pw': user_password}

browser = webdriver.Chrome()
browser.get('https://www.bidrl.com/login')
browser.set_window_position(0, 0)
browser.maximize_window()
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

#go to invoices page, set records per page to 36
time.sleep(2)
browser.get('https://www.bidrl.com/myaccount/invoices')
perpage = browser.find_element(By.ID, 'perpage-top')
actions = ActionChains(browser)
actions.move_to_element(perpage).click()
actions.send_keys("3")
actions.send_keys(Keys.ENTER)
actions.perform()


'''
# gather list of invoice links

# gather list of all elements with tag name "tr"
tr_elements = browser.find_elements(By.TAG_NAME, 'tr')
invoice_links = []
for tr in tr_elements[2:]: # each tr element is an invoice row
    td_elements = tr.find_elements(By.TAG_NAME, 'td') # each td element is an cell in the row basically
    if len(td_elements) > 0:
        for td in td_elements:
            # one of these td "cells" will have an element "a", which contains the link to the invoice.
            # we want to try each cell in the row and, if it contains a link, append it to invoice_links
            try: 
                invoice_links.append(td.find_element(By.TAG_NAME, 'a').get_property('href'))
            except: continue
'''

invoice_links = ['https://www.bidrl.com/myaccount/invoice/invid/3273850'] # for dev


# now that we have our array of links, go into each one and extract the necessary information we need
invoice_info = []
for link in invoice_links:
    print("going to: " + link)
    browser.get(link) # go to invoice link

    # todo: get invoice #

    # todo: get purchase date

    # gather list of all elements with tag name "tr"
    tr_elements = browser.find_elements(By.TAG_NAME, 'tr')
    for tr in tr_elements[2:]: # each tr element is an item row
        print('asdf')
        print (tr.text)



# add input line here to pause the program so I can look at the browser window it has pulled up
input()
