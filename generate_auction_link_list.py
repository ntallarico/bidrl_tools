'''
This script generates a list of auction links, each set to show the maximum items per page.
If todoist_api_token is defined in config.py, then add urls as tasks in Todoist.
'''

import time
from datetime import datetime, date
import bidrl_functions as bf
from config import home_affiliates
from todoist_api_python.api import TodoistAPI
import json


def generate_auction_link_list():
    browser = bf.init_webdriver('headless')
    
    auctions = []
    for aff in home_affiliates:
        auctions.extend(bf.scrape_auctions(browser, affiliate_id = aff, auctions_to_scrape = 'open'))

    auction_urls = []
    for auction in auctions:
        auction_urls.append(auction.url + 'perpage_NjA')
    print("")
    for url in auction_urls:
        print(url)
    print("")

    # check if todoist api is defined in config file, and if it is, proceed with adding urls as tasks in todoist
    try:
        from config import todoist_api_token
    except ImportError:
        todoist_api_token = None

    if not todoist_api_token:
        #print("\ntodoist_api_token is not defined in config.py. Todoist integration.")
        return
    else:
        print("\ntodoist_api_token found in config.py. Proceeding")
        print("Attempting to post URLs to Todoist")

        parent_task_name = 'Review BidRL auctions for this week'

        # Initialize the Todoist API
        api = TodoistAPI(todoist_api_token)

        # Create the parent task
        try:
            parent_task = api.add_task(content=parent_task_name, due_string='today')
            print(f"Parent task created: {parent_task.content}")
        except Exception as error:
            print(f"Error creating parent task: {error}")

        # Create subtasks for each auction URL
        for url in auction_urls:
            try:
                subtask = api.add_task(content=url, parent_id=parent_task.id)
                print(f"Subtask task created (parent ID {parent_task.id}): [...]{subtask.content[-40:]}")
            except Exception as error:
                print(f"Error creating subtask for {url}: {error}")


if __name__ == "__main__":
    start_time = time.time()
    generate_auction_link_list()
    end_time = time.time()
    print("generate_auction_link_list complete. Run time: {:.4f} seconds".format(end_time - start_time))
