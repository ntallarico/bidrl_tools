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


# read in csv with max_desired_bid field input from user

filename_to_read = 'local_files/favorite_items_to_input_max_bid.csv'

fieldnames = ['Auction_Title', 'Item_ID', 'Description', 'Is_Favorite', 'URL', 'Max_Desired_Bid']

read_rows = bf.read_items_from_csv(filename_to_read, fieldnames)

for row in read_rows:
    print(row)



# to do: wait on a loop for the auction end times on each item

    # to do: init window, log in to bidrl, and go to item's page

    # to do: check if "agree to terms" box is present, and if so: check box and hit ok button

    # to do: place bid. ensure that many double checks are in place here for safety!

    # to do: end program when all items that we have entered a max bid for have completed







'''
game plan:
1. have this script scrape all open auctions / items to a csv. scrape_open_auctions_to_csv.py
    - later we can do this with sql or whatever maybe
2. have another script make a copy of that csv, filter it to favorites, and add another column "max price to bid" or whatever
    - this script will also check if that file already exists, and if it does:
        - load in rows from second file, compare it to first, remove rows that aren't present in first
3. at this point - user goes into file created from last script and adds in max desired prices. user will use excel to filter based on is_favorite column
4. auto bid script. this reads in the file from script 2 that is now filled out by the user and wait to bid on items at appropriate time

'''
