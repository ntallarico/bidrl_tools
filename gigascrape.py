import os, sys, getpass, time, re, json, csv, requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from seleniumrequests import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import user_email, user_password, google_form_link_base
from datetime import datetime
from bidrl_classes import Item, Invoice, Auction
from bs4 import BeautifulSoup





'''
questions I'd like to answer in reporting once I have full database:
- what bidding strategy / timing works best? bidding one single time at 2mins out? 10 seconds out? is there a difference on average at all?
    - need to analyze full population's bid history

'''





'''
surveillance project

- I'll need a list of all auction ids
    - brute force?? need to be careful not to DDOS lol
- then from each auction id I'll need a list of all item ids in those auctions
    - possibly an API call for this? like a GetItems or something
- then I'll just need to loop through all auctions, then all items under each auction, then I'll have all the data! easy as that
'''