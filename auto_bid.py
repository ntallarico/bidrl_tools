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


# define class Item_AutoBid that inherits all fields from Item class and adds additional fields used for auto bid process
# adds fields related to the concept of an item bid group. These are used in the implementation of the following functionality:
    # the user can specify that multiple items belong to the same group
    # auto_bid will only attempt to win x amount of these items and no more
    # for example: we want to win a bike. 6 bikes are listed on the auction. the user can assign all 6 bikes the same item_bid_group_id
        # and set items_in_bid_group_to_win to 1, and this script will continue to bid on every bike in the group until exactly 1
        # bike has been won by the user's account, and then not bid on any further bikes in the list
class Item_AutoBid(Item):
    def __init__(self
                 , has_autobid_been_placed: int = None
                 , items_in_bid_group: int = None # num of items in the same bid group
                 , items_in_bid_group_won: int = None # num of items in same group that we won / are winning
                 , items_in_bid_group_to_win: int = None # num of items in a bid group that we intend to win
                 #, max_desired_bid: float = None
                 #, item_bid_group_id: str = None
                 , *args, **kwargs):
        
        super().__init__(*args, **kwargs) # call the constructor of the base Item class

        if has_autobid_been_placed is not None and not isinstance(has_autobid_been_placed, int):
            raise TypeError(f"Expected has_autobid_been_placed to be int, got {type(id).__name__}")
        if items_in_bid_group is not None and not isinstance(items_in_bid_group, int):
            raise TypeError(f"Expected items_in_bid_group to be int, got {type(id).__name__}")
        if items_in_bid_group_won is not None and not isinstance(items_in_bid_group_won, int):
            raise TypeError(f"Expected items_in_bid_group_won to be int, got {type(id).__name__}")
        if items_in_bid_group_to_win is not None and not isinstance(items_in_bid_group_to_win, int):
            raise TypeError(f"Expected items_in_bid_group_to_win to be int, got {type(id).__name__}")
        #if max_desired_bid is not None and not isinstance(max_desired_bid, float):
            #raise TypeError(f"Expected max_desired_bid to be float, got {type(max_desired_bid).__name__}")
        #if item_bid_group_id is not None and not isinstance(item_bid_group_id, str):
            #raise TypeError(f"Expected item_bid_group_id to be str, got {type(item_bid_group_id).__name__}")
        
        self.has_autobid_been_placed = has_autobid_been_placed
    
    def display(self):
        print(f"Still need to bid?: {self.has_autobid_been_placed}")
        #print(f"Max Desired Bid: {self.max_desired_bid}")
        #print(f"Item Bid Group ID: {self.item_bid_group_id}")


def convert_seconds_to_time_string(seconds):
    days, seconds = divmod(seconds, 86400)  # 60 seconds * 60 minutes * 24 hours
    hours, seconds = divmod(seconds, 3600)  # 60 seconds * 60 minutes
    minutes, seconds = divmod(seconds, 60)
    time_string = ''

    if days > 0:
        time_string += f"{days}d, "

    if hours > 0:
        time_string += f"{hours}h, "

    if minutes > 0:
        time_string += f"{minutes}m, "

    if seconds >= 0:
        time_string += f"{seconds}s"
    return time_string


# return current system time in unix format
def time_unix():
    return int(time.time())


# return system format in format "4/29 11:15am"
def time_formatted():
    system_time = datetime.now() # get current system time
    format_1 = system_time.strftime("%m/%d/%y %I:%M%p").lower() # format system time as desired
    format_2 = format_1.lstrip("0").replace("/0", "/") # remove leading zeros
    return format_2


# updates select item info in a list of item objects
# requires: webdriver object, list of item objects
# returns: nothing
# changes: item objects in list
def update_item_info(browser, items):
    try:
        print("Updating item data from bidrl.")

        # get distinct list of auction_ids from items list
        auction_ids = []
        for item in items:
            if item.auction_id not in auction_ids:
                auction_ids.append(item.auction_id)

        new_items = []
        # fast scrape all items from all auctions in list
        for auction_id in auction_ids:
            scraped_items = bf.scrape_items_fast(browser, auction_id, get_images = 'false')
            new_items.extend(scraped_items) # union lists together into new_items
        
        # update fields in items list
        for item in items:
            for new_item in new_items:
                if new_item.id == item.id:
                    item.end_time_unix = new_item.end_time_unix
                    item.highbidder_username = new_item.highbidder_username
                    item.bidding_status = new_item.bidding_status

        print("Success.")
        return 0
    except Exception as e:
        print(f"update_item_info() failed with exception: {e}")
        return 1
    

# updates item info pertaining to item bid groups
# loops through list of items, then loops through another list of items for searching
# if search item is in same bid group as our item, then iterate items_in_bid_group
# if search item is in the same bid group as our item and we're winning it, then iterate items_in_bid_group_won
def update_item_group_info(browser, items, username):
    update_item_info(browser, items)
    print("Updating item group info.")
    for item in items:
        item.items_in_bid_group_won = 0
        item.items_in_bid_group = 0
        for item_search in items:
            # check if this other item is in the same bid group
            if item.item_bid_group_id == item_search.item_bid_group_id and item.id != item_search.id:
                item.items_in_bid_group += 1
                # check and see if we already won this other item that is in the same bid group
                if item_search.highbidder_username == username:
                    item.items_in_bid_group_won += 1
    return 0


def create_item_objects_from_rows(item_rows_list):
    item_list = [] # list for item objects to return at the end
    for item_row in item_rows_list:
        # check if max_desired_bid is not empty. if it isn't, then convert to float. if it is, then set to None
        max_desired_bid = float(item_row['max_desired_bid']) if item_row['max_desired_bid'] != '' else None

        # extract data from json into temp dictionary to create item with next
        temp_item_dict = {'id': item_row['item_id']
                                , 'auction_id': item_row['auction_id']
                                , 'description': item_row['description']
                                , 'url': item_row['url']
                                , 'end_time_unix': int(item_row['end_time_unix'])
                                , 'max_desired_bid': max_desired_bid
                                , 'item_bid_group_id': item_row['item_bid_group_id']
                                , 'has_autobid_been_placed': 0
                                , 'items_in_bid_group_to_win': 1
                                }
        
        item_list.append(Item_AutoBid(**temp_item_dict))
    return item_list


# read favorite_items_to_input_max_bid.csv and return list of item objects for items where max_desired_bid > 0
def read_user_input_csv_to_item_objects(browser):
    try:
        filename = 'favorite_items_to_input_max_bid.csv'
        path_to_file = 'local_files/'

        file_path = path_to_file + filename

        fieldnames = ['end_time_unix', 'auction_id', 'item_id', 'item_bid_group_id', 'description', 'max_desired_bid', 'url']

        read_rows = bf.read_items_from_csv(file_path, fieldnames)

        item_list = create_item_objects_from_rows(read_rows)

        #items_to_bid_on = []
        item_count_with_desired_bid = 0
        item_count_zero_desired_bid = 0
        item_count_no_desired_bid = 0
        for item in item_list:
            if item.max_desired_bid == 0:
                item_count_zero_desired_bid += 1
            elif item.max_desired_bid == None:
                item_count_no_desired_bid += 1
            else:
                item_count_with_desired_bid += 1
                #items_to_bid_on.append(item)

        print(f"\nRead file: {filename}.")
        print(f"Items with max_desired_bid: {item_count_with_desired_bid}")
        print(f"Items without max_desired_bid: {item_count_no_desired_bid}")
        print(f"Items with 0 max_desired_bid: {item_count_zero_desired_bid}\n")

        # sort list of items in descending order based on their end time
        item_list.sort(key=lambda x: x.end_time_unix, reverse=True)

        return item_list
    except Exception as e:
        print(f"read_user_input_csv_to_item_objects() failed with exception: {e}")
        print("Tearing down web object.")
        browser.quit()
        return 1

# need to finish implementing this using getsession from api but for now this works with my particular username while I work on this
def get_username(browser):
    return user_email[0:3]

def print_items_status(items_to_bid_on):
    print('\n----------------------------------------------------------------------------------------------------')
    current_time_unix = time_unix()
    for item in items_to_bid_on:
        if item.bidding_status != 'Closed' and item.has_autobid_been_placed == 0 and item.items_in_bid_group_won < item.items_in_bid_group_to_win:
            remaining_seconds = item.end_time_unix - current_time_unix
            remaining_time_string = convert_seconds_to_time_string(remaining_seconds)
            print(f"{remaining_time_string} remaining. Intending to bid ${item.max_desired_bid}: {item.description}")
            #print(item.description)
            #print(f"\t{remaining_time_string} remaining. Intending to bid ${item.max_desired_bid}.")
    print('----------------------------------------------------------------------------------------------------')

# loop through each item and bid on it if we determine we should
# checks to see if:
    # time remaining on the item is <= our set seconds_before_closing_to_bid time
    # item is not already closed
    # auto_bid() has not already placed a bid on this item
    # if the item is in a bid group, that more than [item.items_in_bid_group_to_win] have not already been won
def auto_bid(browser, items_to_bid_on, seconds_before_closing_to_bid, username):
    current_time_unix = time_unix()
    # loop through each item and bid on it if the time remaining on the item is <= our set seconds_before_closing_to_bid time
    for item in items_to_bid_on:
        remaining_seconds = item.end_time_unix - current_time_unix
        if remaining_seconds <= seconds_before_closing_to_bid and item.bidding_status != 'Closed' and item.has_autobid_been_placed == 0:
            print(f"{remaining_seconds} seconds remaining. Time to pace bid on: {item.description}.")
            update_item_group_info(browser, items_to_bid_on, username)
            if item.items_in_bid_group_won < item.items_in_bid_group_to_win:
                bf.bid_on_item(item, item.max_desired_bid, browser)
                print('')
                item.has_autobid_been_placed = 1


def login_refresh(browser, last_login_time, last_login_time_unix):
    print(f"Checking login status ({time_formatted()}).")
    if bf.check_if_login_success(browser) != 0:
        print("Login check failed!")
        print("Tearing down webdriver, initiating new webdriver, and starting login process.")
        browser.quit()
        browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
        last_login_time = time_formatted()
        last_login_time_unix = time_unix()
    else:
        logged_in_time = convert_seconds_to_time_string(time_unix() - last_login_time_unix)
        print(f"Login check success. Last login: {last_login_time}. Time remained logged in: {logged_in_time}.")


def auto_bid_main(seconds_before_closing_to_bid = 120 + 5 # add 5 secs to account for POST time to API. don't want to extend bid time if we can avoid
         , auto_bid__interval = 5 # how often to check if it is time to bid on each item (and then bid if it is)
         , print_items_status__interval = 60 # how often to print times remaining for all items
         , login_refresh__interval = 60 # keep this reasonable - actually submits a request to bidrl
         , update_item_info__interval = 60 * 60 # keep this reasonable - actually submits a request to bidrl
         ):
    
    # get an initialized web driver that has logged in to bidrl with credentials stored in config.py
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
    last_login_time_string = time_formatted()
    last_login_time_unix = time_unix()
    username = get_username(browser)
    print(f"Username: {username}")


    # read favorite_items_to_input_max_bid.csv and return list of item objects we intend to bid on
    items_to_bid_on = read_user_input_csv_to_item_objects(browser)

    update_item_group_info(browser, items_to_bid_on, username)

    #remove_closed_items(items_to_bid_on)
    closed_item_count = 0
    for item in items_to_bid_on:
        if item.bidding_status == 'Closed':
            closed_item_count += 1
    print(f"\nItems already closed: {closed_item_count}")

    print(f"\nWe intend to bid on {len(items_to_bid_on) - closed_item_count} items, {seconds_before_closing_to_bid} seconds before they close, checking every {auto_bid__interval} seconds.\n")
    
    # set x__last_run_time to 0 to run immediately when loop processes
    # set to time_unix() to wait x__interval amount of seconds first
    auto_bid__last_run_time = 0
    login_refresh__last_run_time = 0
    print_items_status__last_run_time = 0
    update_item_info__last_run_time = time_unix()

    try:
        # loop until KeyboardInterrupt, testing if it has been x_function__interval seconds since last run of x_function()
        # if it has been, run x_function(), then test the next function and its corresponding times
        while True:
            # update_item_info()
            if time_unix() - update_item_info__last_run_time >= update_item_info__interval:
                update_item_info(browser, items_to_bid_on)
                update_item_info__last_run_time = time_unix()

            # login_refresh()
            if time_unix() - login_refresh__last_run_time >= login_refresh__interval:
                login_refresh(browser, last_login_time_string, last_login_time_unix)
                login_refresh__last_run_time = time_unix()

            # print_items_status()
            if time_unix() - print_items_status__last_run_time >= print_items_status__interval:
                print_items_status(items_to_bid_on)
                print_items_status__last_run_time = time_unix()

            # auto_bid()
            if time_unix() - auto_bid__last_run_time >= auto_bid__interval:
                auto_bid(browser, items_to_bid_on, seconds_before_closing_to_bid, username)
                auto_bid__last_run_time = time_unix()

            time.sleep(1)
    finally:
        print("Loop interrupted. Tearing down browser object and exiting program.")
        browser.quit()


if __name__ == "__main__":
  auto_bid_main()




# new plan:
# in auto_bid, when we see that it is time for an item to be bid on, do the following:
    # check if that item is part of a group with more than one item. if it is not, then straight up just bid on the item
        # run a for loop for this to get all bid group ids that share that item's bidgroupid
    # if it is, then we now have a list of the other items with that item's bidgroupid. run an item data update real quick and do our thing from there
# no itemgroup class needed for this. easy peasy. can go back and delete the itemclass bit.



'''
what we need to to:
- follow above plan. we tried doing a bit with a class for groups and separate group handling and it kinda sucked ass and was a pain. just do it this way
- have scrape_open_auctions_to_csv.py scrape to sql database instead of csv
- update create_user_input_csv.py to read from sql database
- update create_user_input_csv.py to output to google sheet (leave option in code for using csv still? - in case anyone wants to use git repo)
- update auto_bid.py to read from google sheet, re-reading every hour or whatever

'''






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