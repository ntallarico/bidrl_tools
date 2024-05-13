'''
This script generates a list of auction links, each set to show the maximum items per page.
'''

import time
from datetime import datetime
import bidrl_functions as bf


def generate_auction_link_list():
    browser = bf.init_webdriver('headless')
    auctions = bf.scrape_auctions(browser, affiliate_id = '47', auctions_to_scrape = 'open')
    auction_urls = []
    for auction in auctions:
        auction_urls.append(auction.url + 'perpage_NjA')
    print("")
    for url in auction_urls:
        print(url)
    print("")


if __name__ == "__main__":
    start_time = time.time()
    generate_auction_link_list()
    end_time = time.time()
    print("generate_auction_link_list complete. Run time: {:.4f} seconds".format(end_time - start_time))