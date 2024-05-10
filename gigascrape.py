import os, sys, getpass, time, re, json, csv, requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from seleniumrequests import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import user_email, user_password, sql_server_name, sql_database_name, sql_admin_username, sql_admin_password
from datetime import datetime
from bidrl_classes import Item, Invoice, Auction
import bidrl_functions as bf
import pyodbc


'''
### step 1:
send a POST request to: https://www.bidrl.com/api/auctions
with payload:
    {
        "filters[startDate]": 04/11/2024
        "filters[endDate]": 05/10/2024
        "filters[perpage]": 100
        "past_sales": true
    }

from this, we get all of our auction urls and ids, and any other information that can be filled in about an auction



### step 2:
go through each auction entry and send a POST request to: https://www.bidrl.com/api/getitems
with payload:
    {
        "auction_id": auction_id,
        "filters[perpage]": 10000
    }

from this, we get all of our item urls and ids

technically, I could get a lot more item data in this step and entirely skip step 3, but I wouldn't be able to get all the item data.
this leaves me with the decision, do I:
1. gather almost all the item data in this step, making the entire scraping operation immensely faster, then provide the option
to fill in the remaining item data with an additional script that calls step 3
2. gather only item urls and ids in this step, then gather all the item data in step 3
I assume that adding in more fields grabbed in a step adds some marginal amount of time. so whether that time is added in step 2 or 3 doesn't make
a difference in the overall execution of all 3 steps. However, adding it in step 2 would allow me the option to do an only step 1 and 2



### step 3:
go through each item and send a POST request to https://www.bidrl.com/api/ItemData
with payload:
    {
        "item_id": extracted_ids['item_id'],
        "auction_id": extracted_ids['auction_id']
    }

from this, we get all of our item data including bid history for each item





'''


conn = bf.init_sql_connection(sql_server_name, sql_database_name, sql_admin_username, sql_admin_password)

cursor = conn.cursor()



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