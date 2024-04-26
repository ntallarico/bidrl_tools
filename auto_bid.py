'''
Goal:
1. Script scrapes entirely of favorited items list into csv
    - this is done by scrape_favorite_items.py
2. User opens csv and inputs a max bid price for each item
3. Script attempts to bid max price on each item 2 minutes before end time
    - this is done by this script


need to determine optimal time to bid.

- definitively, less than 5 mins
- maybe just before 2 mins?
- I feel that if we bid at say 15 seconds, then the person that was 'winning' it from 2 mins to 15 secs would feel in their heart like it was theirs.
    You get that spike at < 30 secs where it's like "oh nobody is going to snipe this at this point, this is mine"
    I feel bidding past that point would lead to us getting outbid by people that are now suddenly more attached to the item
- however maybe if someone is going to outbid to win it, they are going to anyway
- maybe there are several kinds of bidders. lets list a few we can think of, and then determine how we can out bid each
    - bidder that bids way ahead of time and leaves it
        - this kind of bidder loses most of the time
        - doing this just sets the table for the "oo what's it going for" kind of bidder, and ultimately just gets serge more money
    - bidder that puts in their max bid 5 mins out
    - bidders that are not firm on their max bid and keep inching it up
        - bidder that is emotionally attached to their item
            they've thought about where they want to put it in their house and pictured it there
            they started thinking about this when the price was at $1.25 and that thought was just part of their decision making process,
            but now it's night-of, and it's at $7, and they've been picturing holding it in their hands for a while...
        - bidders with simply no goddamn self control and want to win for the high of it. impulsive people.
            "oh just $0.25 more and I could see the Green Message"
    - bidders that ask "oo what's it going for" before determining their max price

'''

import os, sys, getpass
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from config import user_email, user_password, google_form_link_base
from datetime import datetime
import bidrl_functions as bf
from bidrl_classes import Item, Invoice, Auction


def convert_seconds_to_time_string(seconds):
    days, seconds = divmod(seconds, 86400)  # 60 seconds * 60 minutes * 24 hours
    hours, seconds = divmod(seconds, 3600)  # 60 seconds * 60 minutes
    minutes, seconds = divmod(seconds, 60)
    time_string = ''

    if days > 0:
        time_string += f"{days}D, "

    if hours > 0:
        time_string += f"{hours}H, "

    if minutes > 0:
        time_string += f"{minutes}M, "

    if seconds > 0:
        time_string += f"{seconds}S"
    return time_string


# read in csv with max_desired_bid field input from user

filename_to_read = 'local_files/favorite_items_to_input_max_bid.csv'

fieldnames = ['end_time_unix', 'auction_id', 'item_id', 'description', 'max_desired_bid', 'url']

read_rows = bf.read_items_from_csv(filename_to_read, fieldnames)


def create_item_objects_from_rows(item_rows_list):
    item_list = [] # list for item objects to return at the end
    for item_row in item_rows_list:
        #print(item_row)

        # extract data from json into temp dictionary to create item with later
        temp_item_dict = {'id': item_row['item_id']
                                , 'auction_id': item_row['auction_id']
                                , 'description': item_row['description']
                                , 'url': item_row['url']
                                , 'end_time_unix': item_row['end_time_unix']
                                , 'max_desired_bid': item_row['max_desired_bid']}
        
        item_list.append(Item(**temp_item_dict))
    return item_list


item_list = create_item_objects_from_rows(read_rows)

items_to_bid_on = []
item_count_with_desired_bid = 0
item_count_zero_desired_bid = 0
item_count_no_desired_bid = 0
for item in item_list:
    if item.max_desired_bid == '0':
        item_count_zero_desired_bid += 1
    elif item.max_desired_bid != '':
        item_count_with_desired_bid += 1
        items_to_bid_on.append(item)
        print('')
        print(f"item_id: {item.id}")
        print(f"auction_id: {item.auction_id}")
        print(f"description: {item.description}")
        print(f"url: {item.url}")
        print(f"end_time_unix: {item.end_time_unix}")
        print(f"max_desired_bid: {item.max_desired_bid}")
    else:
        item_count_no_desired_bid += 1

print('')
print(f"Items with max_desired_bid: {item_count_with_desired_bid}")
print(f"Items without max_desired_bid: {item_count_no_desired_bid}")
print(f"Items with 0 max_desired_bid: {item_count_zero_desired_bid}")


# sort list of items in ascending order based on their end time
items_to_bid_on.sort(key=lambda x: x.end_time_unix)


# get an initialized web driver that has logged in to bidrl with credentials stored in config.py
browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')



# how often to check times (in seconds)?
refresh_rate = 10

# how soon before closing to bid (in seconds)?
# I add 5 seconds to give api time to post bid so that I don't risk extending bidding time (even by a second or two)
# I add refresh_rate seconds to account for worst case scenario - example:
    # refresh_rate is 10 secs. loop refreshes at 2m 1s out, bid wouldn't be placed until 1m 51s, therefore extending the bid time by 9 seconds
    # we want the absolute minimum amount of seconds before close after we place our bid
seconds_before_closing = 60 * 2 + refresh_rate + 5 # 2 mins 5 secs



print(f"\nWe intend to bid on {item_count_with_desired_bid} items, {seconds_before_closing} seconds before they close, checking every {refresh_rate} seconds.\n")


# every refresh_rate seconds, check each item to see if it is time to bid
# if it is, bid on it and remove it from the bid list
# once the list is empty, end the loop
while len(items_to_bid_on) > 0:
    current_unix_time = int(time.time()) # get unix time

    for item in items_to_bid_on:
        remaining_seconds = int(item.end_time_unix) - current_unix_time
        remaining_time_string = convert_seconds_to_time_string(remaining_seconds)
        print(f"{remaining_time_string} remaining on item: {item.description}")
        
        # bid on the item if time remaining on item is <= our set seconds_before_closing time
        if remaining_seconds <= seconds_before_closing:
            bf.bid_on_item(item, item.max_desired_bid, browser)
            print('')
            items_to_bid_on.remove(item)

    print('')
    time.sleep(10)

print("No remaining items in bid list with max_desired_bid set. Exiting program.")
browser.quit()

