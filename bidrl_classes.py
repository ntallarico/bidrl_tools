# This file defines all of our classes. Concepts like Item and Invoice which will act as components in our data structures
# Invoice holds a list of Item class instances


# define Item class to hold all of our information about a given item
class Item:
    def __init__(self
                 , id=''
                 , auction_id=''
                 , description=''
                 , tax_rate=''
                 , buyer_premium=''
                 , current_bid=''
                 , url=''
                 , highbidder_username=''
                 , lot_number=''
                 , bidding_status=''
                 , end_time_unix=''
                 , is_favorite=''
                 , bid_count=''
                 , total_cost=''
                 , cost_split=''
                 , max_desired_bid=''):
        self.id = id
        self.auction_id = auction_id
        self.description = description
        self.tax_rate = tax_rate # ex: '0.06' for 6% ### need to actually implement this. currently holding a string like '6.000% - 0.22'
        self.buyer_premium = buyer_premium # ex: '0.13' for 13%
        self.current_bid = current_bid
        self.url = url
        self.highbidder_username = highbidder_username
        self.lot_number = lot_number
        self.bidding_status = bidding_status
        self.end_time_unix = end_time_unix
        self.is_favorite = is_favorite
        self.bid_count = bid_count
        self.total_cost = total_cost # calculated total cost based on current_bid, tax rate, and buyer_premium
        self.cost_split = cost_split
        self.max_desired_bid = max_desired_bid

    def display(self):
        print(f"ID: {self.id}")
        print(f"Auction ID: {self.auction_id}")
        print(f"Description: {self.description}")
        print(f"Tax Rate: {self.tax_rate}")
        print(f"Buyer Premium: {self.buyer_premium}")
        print(f"Current Bid: {self.current_bid}")
        print(f"URL: {self.url}")
        print(f"High Bidder Username: {self.highbidder_username}")
        print(f"Lot Number: {self.lot_number}")
        print(f"Bidding Status: {self.bidding_status}")
        print(f"End Time Unix: {self.end_time_unix}")
        print(f"Is Favorite: {self.is_favorite}")
        print(f"Bid Count: {self.bid_count}")
        print(f"Total Cost: {self.total_cost}")
        print(f"Cost Split: {self.cost_split}")
        print(f"Max Desired Bid: {self.max_desired_bid}")


# define Invoice class to hold all of our information about a given invoice
# Invoice class will contain a list of Item classes
class Invoice:
    def __init__(self, id='', date='', link='', items=None, total_cost='', expense_input_form_link=''):
        self.id = id
        self.date = date
        self.link = link
        self.items = items if items is not None else [] # "this solves a poblem in python with mutable arguments and avoids potential bugs" - AI
        self.total_cost = total_cost
        self.expense_input_form_link = expense_input_form_link

    def add_item(self, item):
        self.items.append(item)

    def display(self):
        print(f"Invoice ID: {self.id}, Date: {self.date}, Link: {self.link}, Total Cost: {self.total_cost}, Expense Input Form Link: {self.expense_input_form_link}")
        print("Items:")
        for item in self.items:
            item.display()


# define Auction class to hold all of our information about a given auction
# Auction class will contain a list of Item classes
class Auction:
    def __init__(self, id='', url='', items=None, title = '', item_count = '', start_datetime = '', status = ''):
        self.id = id
        self.url = url
        self.items = items if items is not None else []
        self.title = title
        self.item_count = item_count
        self.start_datetime = start_datetime
        self.status = status

    def add_item(self, item):
        self.items.append(item)

    def display(self):
        print(f"Auction ID: {self.id}")
        print(f"Title: {self.title}")
        print(f"URL: {self.url}")
        print(f"Item Count: {self.item_count}")
        print(f"Start Date: {self.start_datetime}")
        print(f"Status: {self.status}")
        print("Items:")
        for item in self.items:
            item.display()

