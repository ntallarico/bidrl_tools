import os, csv
from config import user_email, user_password
from datetime import datetime
import bidrl_functions as bf


auto_bid_folder_path = 'local_files/auto_bid/'
bf.ensure_directory_exists(auto_bid_folder_path)

filename_to_write = auto_bid_folder_path + 'favorite_items_to_input_max_bid.csv'

# check if the file already exists and ask for user input to confirm overwriting it if it does
if os.path.exists(filename_to_write):
    user_input = input(f"\nThe file '{filename_to_write}' already exists, possibly with your max bids in it. Do you want to overwrite it? (y/n): ")
    
    if user_input.lower() != 'y':
        print("File will not be overwritten. Exiting.")
        quit()
    else:
        print(f"Will overwrite '{filename_to_write}'.")
else:
    print(f"Creating '{filename_to_write}'.")


 # get an initialized web driver that has logged in to bidrl with credentials stored in config.py
browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless')


# use get_open_auctions_fast() to get abridged version of all open auction/item data for our chosen affiliate
open_auctions = bf.get_open_auctions_fast(browser, affiliate_id = '47')

print(f"\nFinding favorites from {len(open_auctions)} auctions.")
rows_to_write = []
for auction in open_auctions:
    for item in auction.items:
        if item.is_favorite == 1:
            try:
                rows_to_write.append({
                    'end_time_unix': item.end_time_unix,
                    'auction_id': auction.id,
                    'item_id': item.id,
                    'item_bid_group_id': item.id,
                    'description': item.description,
                    'max_desired_bid': '',  # placeholder for user input
                    'url': item.url
                })
                print(f"Found favorite: {item.description}")
            except Exception as e:
                print(f"Failed on item: {item.description}")
                print(f"Exception: {e}")
                bf.tear_down(browser)
print(f"\nFound {len(rows_to_write)} favorites.")

try:
    with open(filename_to_write, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(['end_time_unix', 'auction_id', 'item_id', 'item_bid_group_id', 'description', 'max_desired_bid', 'url']) # write the header, adding "Max Desired Bid"

        # write item data
        for row in rows_to_write:
            writer.writerow([row['end_time_unix'], row['auction_id'], row['item_id'], row['item_id'], row['description'], '', row['url']])
    print(f"\nFile successfully written: {filename_to_write}")
except Exception as e:
    print(f"Attempt to write to csv failed.")
    print(f"Exception: {e}")
    bf.tear_down(browser)


bf.tear_down(browser)