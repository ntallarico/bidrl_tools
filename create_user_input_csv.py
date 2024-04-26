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
import csv







fieldnames = ['Auction Title', 'Item ID', 'Description', 'Is Favorite', 'URL']
filename = 'local_files/items.csv'

rows = bf.read_items_from_csv(filename, fieldnames)

# display the read rows
for row in rows:
    print(row)