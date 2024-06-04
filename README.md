# bidrl_tools

Set of tools for usage of BidRL. Scraping, processing of invoices, etc.

**This contains python code that will use your actual user account to bid real money on items. This is a constant work in progress. It is not perfect. Please review code carefully and use at your own risk.**

Setup:
1. Ensure that python is installed.
2. Create file `config.py` in repo. Populate it according to the below details/example:

	Details:
		user_email: your email used for logging into bidrl
	    user_password: your password used for logging into bidrl
	    home_affiliates = list of IDs for affiliates you care about, each in single quotes and separated by commas, and the whole list surrounded by brackets. run list_affiliates.py for name/ID list. for example, if you live in Indiana, you would likely input: `home_affiliates = ['56', '60', '44']`

	Example:
	
	    user_email = 'email@example.com'
	    user_password = 'exampleP@ssw0rd'
	    home_affiliates = ['56', '60', '44']

4. Run `setup.py`


Auto Bid
-

1. Log in to https://www.bidrl.com/ and favorite items.
2. Run scrape_favorites_to_csv.py
3. Open favorite_items_to_input_max_bid.csv and do the following:
	1. Review each item and write what you would like to bid on each item in max_desired_bid column
	2. If there is a group of items that you favorited with the intention to try to just win 1 of, this functionality is handled by the item_bid_group_id column. Set the value for all items in the group to same item_bid_group_id. The item_bid_group_id chosen should be the one from the first item in the group. These items do not all have to be next to eachother, they just all have to have the same item_bid_group_id. The auto bid script we run will ensure that no more than 1 item from each group will end up being purchased (ideally, we still may end up losing them all of course). Set max_desired_bid for each item in the group as normal. Different values for max_desired_bid for each item in a group is allowed if desired.
4. Run auto_bid_orchestrator.py. This script will run auto_bid.py, monitor it to ensure that it is always running, and restart it if it ever isn't. This is to account for any bugs in auto_bid.py that may cause it to crash and is useful for running this script long term, like all week while the auctions run.


Scraping and Data Analysis
-

- `gigascrape.py`
	- Scrapes all data from bidrl into a relational database (bidrl.db) stored in local_files.
	- Optional: you can view the sqlite database using a tool like https://sqlitebrowser.org/dl/
- `dump_database_to_csvs.py`
	- Dumps all information from the database (populated by `gigascrape.py`) into csv files in the local_files/data_analysis/ folder.
	- This must be run before attempting to open any of the Tableau workbooks.
- Tableau workbooks in local_files/data_analysis/ folder
	- These contain our analyses and visualizations of the data we scraped from bidrl using `gigascrape.py`. To use them, first run gigascrape, then dump_database_to_csvs, then open!