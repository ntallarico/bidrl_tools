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


# scrape item objects from bidrl based on list of item_id/auction_id read in from csv.
# we do this because we want the most up-to-date information for these items, like end_time_unix
def scrape_item_objects_from_rows(browser, item_rows_list):
    print("Scraping item objects based on item_id and auction_id read from csv.")
    try:
      item_list = [] # list for item objects to return at the end
      for item_num, item_row in enumerate(item_rows_list):
          item_obj = bf.get_item_with_ids(browser, item_row['item_id'], item_row['auction_id'], get_bid_history = 'false')

          # check if max_desired_bid is not empty. if it isn't, then convert to float. if it is, then set to None
          item_obj.max_desired_bid = float(item_row['max_desired_bid']) if item_row['max_desired_bid'] != '' else None

          print(f"Item object scraped ({item_num + 1}/{len(item_rows_list)}): {item_obj.description}")
          item_list.append(item_obj)
      return item_list
    except Exception as e:
        print(f"scrape_item_objects_from_rows() failed with exception: {e}")
        print("Tearing down web object.")
        browser.quit()
        return 1
        


# read favorite_items_to_input_max_bid.csv and return list of item objects for items where max_desired_bid > 0
def read_user_input_csv(browser):
    try:
        filename = 'favorite_items_to_input_max_bid.csv'
        path_to_file = 'local_files/'

        file_path = path_to_file + filename

        fieldnames = ['end_time_unix', 'auction_id', 'item_id', 'description', 'max_desired_bid', 'url']

        read_rows = bf.read_items_from_csv(file_path, fieldnames)

        item_list = scrape_item_objects_from_rows(browser, read_rows)

        items_to_bid_on = []
        item_count_with_desired_bid = 0
        item_count_zero_desired_bid = 0
        item_count_no_desired_bid = 0
        item_count_already_closed = 0
        for item in item_list:
            if item.max_desired_bid == 0:
                item_count_zero_desired_bid += 1
            elif item.max_desired_bid == None:
                item_count_no_desired_bid += 1
            else:
                item_count_with_desired_bid += 1
                if item.bidding_status == 'Closed':
                    item_count_already_closed += 1
                else:
                    items_to_bid_on.append(item)

        print(f"\nRead file: {filename}.")
        print(f"Items with max_desired_bid: {item_count_with_desired_bid}")
        print(f"Items with max_desired_bid that already closed: {item_count_already_closed}")
        print(f"Items without max_desired_bid: {item_count_no_desired_bid}")
        print(f"Items with 0 max_desired_bid: {item_count_zero_desired_bid}\n")

        # sort list of items in descending order based on their end time
        items_to_bid_on.sort(key=lambda x: x.end_time_unix, reverse=True)

        return items_to_bid_on
    except Exception as e:
        print(f"read_user_input_csv() failed with exception: {e}")
        print("Tearing down web object.")
        browser.quit()
        return 1
    


def print_items_status(items_to_bid_on):
    print('\n----------------------------------------------------------------------------------------------------')
    current_time_unix = time_unix()
    for item in items_to_bid_on:
        remaining_seconds = item.end_time_unix - current_time_unix
        remaining_time_string = convert_seconds_to_time_string(remaining_seconds)
        print(f"{remaining_time_string} remaining. Intending to bid ${item.max_desired_bid}: {item.description}")
        #print(item.description)
        #print(f"\t{remaining_time_string} remaining. Intending to bid ${item.max_desired_bid}.")
    print('----------------------------------------------------------------------------------------------------')


def auto_bid(browser, items_to_bid_on, seconds_before_closing_to_bid):
    current_time_unix = int(time.time())
    # loop through each item and bid on it if the time remaining on the item is <= our set seconds_before_closing_to_bid time
    for item in items_to_bid_on:
        remaining_seconds = item.end_time_unix - current_time_unix
        if remaining_seconds <= seconds_before_closing_to_bid:
            bf.bid_on_item(item, item.max_desired_bid, browser)
            print('')
            items_to_bid_on.remove(item)


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


def auto_bid_main(seconds_before_closing_to_bid # add 5 secs to account for POST time to API. don't want to extend bid time if we can avoid
         , auto_bid__interval # how often to check if it is time to bid on each item (and then bid if it is)
         , print_items_status__interval # how often to print times remaining for all items
         , login_refresh__interval # we want to keep this reasonable because it actually submits a request to bidrl
         ):
    
    # get an initialized web driver that has logged in to bidrl with credentials stored in config.py
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')
    last_login_time_string = time_formatted()
    last_login_time_unix = time_unix()

    # read favorite_items_to_input_max_bid.csv and return list of item objects we intend to bid on
    items_to_bid_on = read_user_input_csv(browser)

    print(f"\nWe intend to bid on {len(items_to_bid_on)} items, {seconds_before_closing_to_bid} seconds before they close, checking every {auto_bid__interval} seconds.\n")
    
    

    # set x__last_run_time to 0 to run immediately when loop processes
    # set to time_unix() to wait x__interval amount of seconds first
    auto_bid__last_run_time = 0
    login_refresh__last_run_time = 0
    print_items_status__last_run_time = 0

    try:
        # loop until KeyboardInterrupt, testing if it has been x_function__interval seconds since last run of x_function()
        # if it has been, run x_function(), then test the next function and its corresponding times
        while True:
            # check if time to run: login_refresh()
            if time_unix() - login_refresh__last_run_time >= login_refresh__interval:
                login_refresh(browser, last_login_time_string, last_login_time_unix)
                login_refresh__last_run_time = time_unix()

            # check if time to run: print_items_status()
            if time_unix() - print_items_status__last_run_time >= print_items_status__interval:
                print_items_status(items_to_bid_on)
                print_items_status__last_run_time = time_unix()

            # check if time to run: auto_bid()
            if time_unix() - auto_bid__last_run_time >= auto_bid__interval:
                auto_bid(browser, items_to_bid_on, seconds_before_closing_to_bid)
                auto_bid__last_run_time = time_unix()

            time.sleep(1)
    finally:
        print("Loop interrupted. Tearing down browser object and exiting program.")
        browser.quit()


if __name__ == "__main__":
  auto_bid_main(seconds_before_closing_to_bid = 120 + 5
          , auto_bid__interval = 5
          , print_items_status__interval = 60
          , login_refresh__interval = 60)





r"""
1/16 Wire Rope Kit Factory Sealed
        10m, 53s remaining. Intending to bid $3.
----------------------------------------------------------------------------------------------------
Checking login status.
Traceback (most recent call last):
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\urllib3\connectionpool.py", line 467, in _make_request
    self._validate_conn(conn)
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\urllib3\connectionpool.py", line 1099, in _validate_conn
    conn.connect()
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\urllib3\connection.py", line 653, in connect
    sock_and_verified = _ssl_wrap_socket_and_match_hostname(
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\urllib3\connection.py", line 806, in _ssl_wrap_socket_and_match_hostname
    ssl_sock = ssl_wrap_socket(
               ^^^^^^^^^^^^^^^^
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\urllib3\util\ssl_.py", line 465, in ssl_wrap_socket
    ssl_sock = _ssl_wrap_socket_impl(sock, context, tls_in_tls, server_hostname)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\urllib3\util\ssl_.py", line 509, in _ssl_wrap_socket_impl
    return ssl_context.wrap_socket(sock, server_hostname=server_hostname)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\ssl.py", line 517, in wrap_socket
    return self.sslsocket_class._create(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\ssl.py", line 1108, in _create
    self.do_handshake()
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\ssl.py", line 1379, in do_handshake
    self._sslobj.do_handshake()
TimeoutError: [WinError 10060] A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed 
because connected host has failed to respond

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\requests\adapters.py", line 486, in send
    resp = conn.urlopen(
           ^^^^^^^^^^^^^
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\urllib3\connectionpool.py", line 847, in urlopen
    retries = retries.increment(
              ^^^^^^^^^^^^^^^^^^
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\urllib3\util\retry.py", line 470, in increment
    raise reraise(type(error), error, _stacktrace)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\urllib3\util\util.py", line 39, in reraise
    raise value
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\urllib3\connectionpool.py", line 793, in urlopen
    response = self._make_request(
               ^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\urllib3\connectionpool.py", line 491, in _make_request
    raise new_e
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\urllib3\connectionpool.py", line 469, in _make_request
    self._raise_timeout(err=e, url=url, timeout_value=conn.timeout)
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\urllib3\connectionpool.py", line 370, in _raise_timeout
    raise ReadTimeoutError(
urllib3.exceptions.ReadTimeoutError: HTTPSConnectionPool(host='www.bidrl.com', port=443): Read timed out. (read timeout=None)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "c:\Users\Nick\Stuff\Projects\BidRL\bidrl_tools\auto_bid.py", line 178, in <module>
    main(seconds_before_closing_to_bid = 120 + 5
  File "c:\Users\Nick\Stuff\Projects\BidRL\bidrl_tools\auto_bid.py", line 168, in main
    login_refresh(browser, last_login_time_string, last_login_time_unix)
  File "c:\Users\Nick\Stuff\Projects\BidRL\bidrl_tools\auto_bid.py", line 125, in login_refresh
    if bf.check_if_login_success(browser) != 0:
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:\Users\Nick\Stuff\Projects\BidRL\bidrl_tools\bidrl_functions.py", line 59, in check_if_login_success
    response = browser.request('GET', 'https://www.bidrl.com/myaccount/myitems')
    response = self.requests_session.request(method, url, **kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\requests\sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\requests\sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Nick\AppData\Local\Programs\Python\Python311\Lib\site-packages\requests\adapters.py", line 532, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='www.bidrl.com', port=443): Read timed out. (read timeout=None)
"""








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