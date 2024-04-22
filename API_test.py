'''
first response in this SO post:
https://stackoverflow.com/questions/77120283/selenium-web-scraping-c-sharp-return-views?newreg=2db9cef1711d49e3be9c50d099154a51


'''

import requests
import json


# item URL
url = "https://www.bidrl.com/auction/high-end-auction-161-johns-rd-unit-a-south-carolina-april-21-152426/item/metal-beads-item-see-pictures-19718242/"






# extract item_id and auction_id from the URL string
# turn this into a function

parts = url.split('/') # Split the URL by '/'

item_id_segment = parts[-2] if url.endswith('/') else parts[-1]
item_id = item_id_segment.split('-')[-1]

auction_id_segment = parts[-4] if url.endswith('/') else parts[-3]
auction_id = auction_id_segment.split('-')[-1]

#print(f"Item ID: {item_id}, Auction ID: {auction_id}")






# get item data from api/ItemData
# turn this into a function


# Create a session object to persist cookies
session = requests.Session()

# Make a GET request to get the cookies
response = session.get(url)

# Make a POST request to login or submit data
post_url = "https://www.bidrl.com/api/ItemData"
post_data = {
    "item_id": item_id,
    "auction_id": auction_id
}

# Sending the POST request with the session that contains the cookies
response = session.post(post_url, data=post_data)

# Ensure the request was successful
response.raise_for_status()

item_data = response.json()

#print(response.text)
#print(response.json())







print(f"ID: {item_data['id']}" + \
    ", Auction ID: {item_data['auction_id']}" + \
    ", Bid Count: {item_data['bid_count']}" + \
    ", Title: {item_data['title']}")

# thoughts:
# it may be faster / easier / more consistent / better to scrape every item on the website
# by scraping all open auctions by id and then scraping all items from all auctions
# and then checking each one for the favorite = 1 property