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


file_path = 'local_files/items.csv'

# Initialize a list to store the rows
rows = []

# Read the CSV file
with open(file_path, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    
    # Check if the header matches the expected header
    if reader.fieldnames == ['Auction Title', 'Item ID', 'Description', 'Is Favorite', 'URL']:
        for row in reader:
            rows.append(row)
    else:
        print("Header row does not match the expected format.")

# Display the read rows
for row in rows:
    print(row)