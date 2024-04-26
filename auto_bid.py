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


item_count_with_desired_bid = 0
item_count_zero_desired_bid = 0
item_count_no_desired_bid = 0
for item in item_list:
    if item.max_desired_bid == '0':
        item_count_zero_desired_bid += 1
    elif item.max_desired_bid != '':
        item_count_with_desired_bid += 1
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


# how many seconds before closing to bid?
seconds_before_closing = 60 * 2 # two minutes
print(f"\nWe intend to bid on {item_count_with_desired_bid} items, {seconds_before_closing} seconds before each closes.")


# to do: wait on a loop for the auction end times on each item
'''while True:
    print('penis')
    time.sleep(10)'''

    # to do: init window, log in to bidrl, and go to item's page

    # to do: check if "agree to terms" box is present, and if so: check box and hit ok button

    # to do: place bid. ensure that many double checks are in place here for safety!

    # to do: end program when all items that we have entered a max bid for have completed



