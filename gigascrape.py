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
import bidrl_functions as bf





import pyodbc



# Set Up Connection


# Connection parameters
server = 'your_server_name'
database = 'BFDB'
username = 'your_username'
password = 'your_password'

# Connection string
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      f'SERVER={server};'
                      f'DATABASE={database};'
                      f'UID={username};'
                      f'PWD={password}')
cursor = conn.cursor()





# Create Tables

cursor.execute('''
CREATE TABLE items (
    item_id INT PRIMARY KEY,
    description NVARCHAR(255),
    auction_id INT,
    end_time_unix BIGINT,
    url NVARCHAR(255)
)
''')
conn.commit()






# Insert Data

def insert_items(items):
    for item in items:
        cursor.execute('''
        INSERT INTO items (item_id, description, auction_id, end_time_unix, url)
        VALUES (?, ?, ?, ?, ?)
        ''', (item['item_id'], item['description'], item['auction_id'], item['end_time_unix'], item['url']))
    conn.commit()

# Example usage
items_data = [{'item_id': 1, 'description': 'Example item', 'auction_id': 101, 'end_time_unix': 1714579800, 'url': 'http://example.com'}]
insert_items(items_data)






# Closing the Connection
conn.close()








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