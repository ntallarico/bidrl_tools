# bidrl_tools

Set of tools for usage of BidRL. Scraping, processing of invoices, etc.

**This is a constant work in progress. This is python code that will use your actual user account to bid real money on items. It is not perfect. Please review code carefully and use at your own risk.**
  

Setup:

1. Ensure that python is installed.
2. Create file config.py in repo. Populate it as such:

		user_email = 'your email'
		user_password = 'your password'
		google_form_link_base = 'google form link for expense input'
		auto_bid_folder_path = 'path to folder where you want to store files used to interface with auto_bid.py script'

3. Run setup.py
4. To scrape all of bidrl's data into a relational database:
	1. Run database_setup.py
	2. Run gigascrape.py
	3. Optional: you can view the sqlite database using a tool like https://sqlitebrowser.org/dl/
5. To use auto bid:
	1. Log in to bidrl.com and favorite items.
	2. Run scrape_open_auctions_to_csv.py
	3. Run create_user_input.csv
	4. Open favorite_items_to_input_max_bid.csv and do the following:
		1. Review each item and write what you would like to bid on each item in max_desired_bid column
		2. If there is a group of items that you favorited with the intention to try to just win 1 of, this functionality is handled by the item_bid_group_id column. Set the value for all items in the group to same item_bid_group_id. The item_bid_group_id chosen should be the one from the first item in the group. These items do not all have to be next to eachother, they just all have to have the same item_bid_group_id. The auto bid script we run will ensure that no more than 1 item from each group will end up being purchased (ideally, we still may end up losing them all of course). Set max_desired_bid for each item in the group as normal. Different values for max_desired_bid for each item in a group is allowed if desired.
5. Run auto_bid_orchestrator.py. This script will run auto_bid.py, monitor it to ensure that it is always running, and restart it if it ever isn't. This is to account for any bugs in auto_bid.py that may cause it to crash and is useful for running this script long term, like all week while the auctions run.