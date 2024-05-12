# This file defines all of our classes. Concepts like Item and Invoice which will act as components in our data structures
# These object structures ensure a standard for each concept across all of our functions and files
# web scraping functions will be responsible for processing scraped data into the correct types/formats for these objects
# once the object is returned, the data should be good to go and consistent going forward


# define Affiliate class to hold all of our information about a given affiliate
class Affiliate:
    def __init__(self
                 , id: int
                 , logo: str
                 , do_not_display_tab: bool
                 , company_name: str
                 , firstname: str
                 , lastname: str
                 , auc_count: int):
        if not isinstance(id, int):
            raise TypeError(f"Expected id to be int, got {type(id).__name__}")
        if not isinstance(logo, str):
            raise TypeError(f"Expected logo to be str, got {type(logo).__name__}")
        if not isinstance(do_not_display_tab, bool):
            raise TypeError(f"Expected do_not_display_tab to be bool, got {type(do_not_display_tab).__name__}")
        if not isinstance(company_name, str):
            raise TypeError(f"Expected company_name to be str, got {type(company_name).__name__}")
        if not isinstance(firstname, str):
            raise TypeError(f"Expected firstname to be str, got {type(firstname).__name__}")
        if not isinstance(lastname, str):
            raise TypeError(f"Expected lastname to be str, got {type(lastname).__name__}")
        if not isinstance(auc_count, int):
            raise TypeError(f"Expected auc_count to be int, got {type(auc_count).__name__}")

        self.id = id
        self.logo = logo
        self.do_not_display_tab = do_not_display_tab
        self.company_name = company_name
        self.firstname = firstname
        self.lastname = lastname
        self.auc_count = auc_count

    def display(self):
        print(f"Affiliate(ID: {self.id}, Company: {self.company_name}, "
                f"First Name: {self.firstname}, Last Name: {self.lastname}, "
                f"Auction Count: {self.auc_count})")


# define Auction class to hold all of our information about a given auction
# Auction class will contain a list of Item classes
class Auction:
    def __init__(self
                 , id: str
                 , url: str
                 , items: list
                 , title: str
                 , item_count: int
                 , start_datetime: str
                 , status: str
                 , affiliate_id: str
                 , aff_company_name: str
                 , state_abbreviation: str
                 , city: str
                 , zip: str
                 , address: str):
        if not isinstance(id, str):
            raise TypeError(f"Expected id to be str, got {type(id).__name__}")
        if not isinstance(url, str):
            raise TypeError(f"Expected url to be str, got {type(url).__name__}")
        if items is not None and not all(isinstance(item, Item) for item in items):
            raise TypeError("All elements in items must be an instance of Item")
        if not isinstance(title, str):
            raise TypeError(f"Expected title to be str, got {type(title).__name__}")
        if not isinstance(item_count, int):
            raise TypeError(f"Expected item_count to be int, got {type(item_count).__name__}")
        if not isinstance(start_datetime, str):
            raise TypeError(f"Expected start_datetime to be str, got {type(start_datetime).__name__}")
        if not isinstance(status, str):
            raise TypeError(f"Expected status to be str, got {type(status).__name__}")
        if not isinstance(affiliate_id, str):
            raise TypeError(f"Expected affiliate_id to be str, got {type(affiliate_id).__name__}")
        if not isinstance(aff_company_name, str):
            raise TypeError(f"Expected aff_company_name to be str, got {type(aff_company_name).__name__}")
        if not isinstance(state_abbreviation, str):
            raise TypeError(f"Expected state_abbreviation to be str, got {type(state_abbreviation).__name__}")
        if not isinstance(city, str):
            raise TypeError(f"Expected city to be str, got {type(city).__name__}")
        if not isinstance(zip, str):
            raise TypeError(f"Expected zip to be str, got {type(zip).__name__}")
        if not isinstance(address, str):
            raise TypeError(f"Expected address to be str, got {type(address).__name__}")

        self.id = id
        self.url = url
        self.items = items if items is not None else []
        self.title = title
        self.item_count = item_count
        self.start_datetime = start_datetime
        self.status = status
        self.affiliate_id = affiliate_id
        self.aff_company_name = aff_company_name
        self.state_abbreviation = state_abbreviation
        self.city = city
        self.zip = zip
        self.address = address

    def add_item(self, item: Item):
        if not isinstance(item, Item):
            raise TypeError(f"Expected item to be an instance of Item, got {type(item).__name__}")
        self.items.append(item)

    def display(self):
        print(f"Auction ID: {self.id}")
        print(f"Title: {self.title}")
        print(f"URL: {self.url}")
        print(f"Item Count: {self.item_count}")
        print(f"Start Date: {self.start_datetime}")
        print(f"Status: {self.status}")
        print(f"Affiliate ID: {self.affiliate_id}")
        print(f"Affiliate Company Name: {self.aff_company_name}")
        print(f"State Abbreviation: {self.state_abbreviation}")
        print(f"City: {self.city}")
        print(f"ZIP: {self.zip}")
        print(f"Address: {self.address}")
        print("Items:")
        for item in self.items:
            item.display()
        

# define Item class to hold all of our information about a given item
# Item class will contain a list of Bid classes
class Item:
    def __init__(self
                 , id: str
                 , auction_id: str
                 , description: str
                 , tax_rate: float
                 , buyer_premium: float
                 , current_bid: float
                 , url: str
                 , highbidder_username: str
                 , lot_number: str
                 , bidding_status: str
                 , end_time_unix: int
                 , bids: list
                 , is_favorite: bool
                 , bid_count: int
                 , viewed: int
                 , total_cost: float
                 , cost_split: str
                 , max_desired_bid: float):
        if not isinstance(id, str):
            raise TypeError(f"Expected id to be str, got {type(id).__name__}")
        if not isinstance(auction_id, str):
            raise TypeError(f"Expected auction_id to be str, got {type(auction_id).__name__}")
        if not isinstance(description, str):
            raise TypeError(f"Expected description to be str, got {type(description).__name__}")
        if not isinstance(tax_rate, float):
            raise TypeError(f"Expected tax_rate to be float, got {type(tax_rate).__name__}")
        if not isinstance(buyer_premium, float):
            raise TypeError(f"Expected buyer_premium to be float, got {type(buyer_premium).__name__}")
        if not isinstance(current_bid, float):
            raise TypeError(f"Expected current_bid to be float, got {type(current_bid).__name__}")
        if not isinstance(url, str):
            raise TypeError(f"Expected url to be str, got {type(url).__name__}")
        if not isinstance(highbidder_username, str):
            raise TypeError(f"Expected highbidder_username to be str, got {type(highbidder_username).__name__}")
        if not isinstance(lot_number, str):
            raise TypeError(f"Expected lot_number to be str, got {type(lot_number).__name__}")
        if not isinstance(bidding_status, str):
            raise TypeError(f"Expected bidding_status to be str, got {type(bidding_status).__name__}")
        if not isinstance(end_time_unix, int):
            raise TypeError(f"Expected end_time_unix to be int, got {type(end_time_unix).__name__}")
        if bids is not None and not all(isinstance(bid, Bid) for bid in bids):
            raise TypeError("All elements in bids must be instances of Bid")
        if not isinstance(is_favorite, bool):
            raise TypeError(f"Expected is_favorite to be bool, got {type(is_favorite).__name__}")
        if not isinstance(bid_count, int):
            raise TypeError(f"Expected bid_count to be int, got {type(bid_count).__name__}")
        if not isinstance(viewed, int):
            raise TypeError(f"Expected viewed to be int, got {type(viewed).__name__}")
        if not isinstance(total_cost, float):
            raise TypeError(f"Expected total_cost to be float, got {type(total_cost).__name__}")
        if not isinstance(cost_split, str):
            raise TypeError(f"Expected cost_split to be str, got {type(cost_split).__name__}")
        if not isinstance(max_desired_bid, float):
            raise TypeError(f"Expected max_desired_bid to be float, got {type(max_desired_bid).__name__}")

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
        self.bids = bids if bids is not None else []
        self.is_favorite = is_favorite
        self.bid_count = bid_count
        self.viewed = viewed
        self.total_cost = total_cost # calculated total cost based on current_bid, tax rate, and buyer_premium
        self.cost_split = cost_split
        self.max_desired_bid = max_desired_bid

    def display(self):
        print(f"\nID: {self.id}")
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
        print(f"Viewed: {self.viewed}")
        print(f"Total Cost: {self.total_cost}")
        print(f"Cost Split: {self.cost_split}")
        print(f"Max Desired Bid: {self.max_desired_bid}")

    def display_bids(self):
        for bid in self.bids:
            bid.display()


# define Bid class to hold all of our information about a given bid
class Bid:
    def __init__(self
                 , bid_id: str
                 , item_id: str
                 , user_name: str
                 , bid: str
                 , bid_time: str
                 , time_of_bid: str
                 , time_of_bid_unix: str
                 , buyer_number: int
                 , description: str):
        if not isinstance(bid_id, str):
            raise TypeError(f"Expected bid_id to be str, got {type(bid_id).__name__}")
        if not isinstance(item_id, str):
            raise TypeError(f"Expected item_id to be str, got {type(item_id).__name__}")
        if not isinstance(user_name, str):
            raise TypeError(f"Expected user_name to be str, got {type(user_name).__name__}")
        if not isinstance(bid, str):
            raise TypeError(f"Expected bid to be str, got {type(bid).__name__}")
        if not isinstance(bid_time, str):
            raise TypeError(f"Expected bid_time to be str, got {type(bid_time).__name__}")
        if not isinstance(time_of_bid, str):
            raise TypeError(f"Expected time_of_bid to be str, got {type(time_of_bid).__name__}")
        if not isinstance(time_of_bid_unix, str):
            raise TypeError(f"Expected time_of_bid_unix to be str, got {type(time_of_bid_unix).__name__}")
        if not isinstance(buyer_number, int):
            raise TypeError(f"Expected buyer_number to be int, got {type(buyer_number).__name__}")
        if not isinstance(description, str):
            raise TypeError(f"Expected description to be str, got {type(description).__name__}")

        self.bid_id = bid_id
        self.item_id = item_id
        self.user_name = user_name
        self.bid = bid
        self.bid_time = bid_time
        self.time_of_bid = time_of_bid
        self.time_of_bid_unix = time_of_bid_unix
        self.buyer_number = buyer_number
        self.description = description

    def display(self):
        print(f"Bid ID: {self.bid_id}")
        print(f"Item ID: {self.item_id}")
        print(f"User Name: {self.user_name}")
        print(f"Bid: {self.bid}")
        print(f"Bid Time: {self.bid_time}")
        print(f"Time of Bid: {self.time_of_bid}")
        print(f"Time of Bid Unix: {self.time_of_bid_unix}")
        print(f"Buyer Number: {self.buyer_number}")
        print(f"Description: {self.description}")


# define Invoice class to hold all of our information about a given invoice
# Invoice class will contain a list of Item classes
class Invoice:
    def __init__(self
                 , id: str
                 , date: str
                 , link: str
                 , items: list
                 , total_cost: float
                 , expense_input_form_link: str):
        if not isinstance(id, str):
            raise TypeError(f"Expected id to be str, got {type(id).__name__}")
        if not isinstance(date, str):
            raise TypeError(f"Expected date to be str, got {type(date).__name__}")
        if not isinstance(link, str):
            raise TypeError(f"Expected link to be str, got {type(link).__name__}")
        if items is not None and not all(isinstance(item, Item) for item in items):
            raise TypeError("All elements in items must be an instance of Item")
        if not isinstance(total_cost, (float, int)):  # Accept int for convenience
            raise TypeError(f"Expected total_cost to be float or int, got {type(total_cost).__name__}")
        if not isinstance(expense_input_form_link, str):
            raise TypeError(f"Expected expense_input_form_link to be str, got {type(expense_input_form_link).__name__}")

        self.id = id
        self.date = date
        self.link = link
        self.items = items if items is not None else []  # "this solves a problem in python with mutable arguments and avoids potential bugs" - AI
        self.total_cost = total_cost
        self.expense_input_form_link = expense_input_form_link

    def add_item(self, item):
        if not isinstance(item, Item):
            raise TypeError(f"Expected item to be an instance of Item, got {type(item).__name__}")
        self.items.append(item)

    def display(self):
        print(f"\n\nInvoice ID: {self.id}, Date: {self.date}, Link: {self.link}, Total Cost: {self.total_cost}, Expense Input Form Link: {self.expense_input_form_link}")
        print("Items:")
        for item in self.items:
            item.display()


            

'''def create_affiliate_list(json_data):
    affiliates = []
    for affiliate in json_data['data'].items():
        affiliate_obj = Affiliate(
            id=affiliate['id'],
            logo=affiliate['logo'],
            do_not_display_tab=affiliate['do_not_display_tab'],
            company_name=affiliate['company_name'],
            firstname=affiliate['firstname'],
            lastname=affiliate['lastname'],
            auc_count=affiliate['auc_count']
        )
        affiliates.append(affiliate_obj)
    return affiliates'''


'''
ok real time
what's my plan for data pipeline
I need to solve a few problems
1. when do I do the conversion of like strings to ints and such
2. when do I do the processing like taking the tax percentage number out of the string. different than step 1?
3. what do I do about field names? item.id or item.item_id?

options
- pull everything into objects raw, then push to sql database and do processing there
- pull everything into objects, processing while scraping, then pass to sql


I think I should process while scraping. any data in an object I define and pass around my functions
should be the final, ideal form. that's the point of my classes here anyway
so tax_rate in Item obect should be a number, 0.06, not a string.

I think that I should have the function that returns that object do the processing for this stuff
once the object is returned, the data should be good to go and consistent going forward.

then I can do like extra info kind of processing in the sql database, like total_cost or whatever


ok, so in order to enact this, what do I need to do
1. I need to set a type on my object variables, making sure that what is placed into them is that type.
    - if something tries to be placed into that object that isn't the right type, an error will be raised.
2. I need to consolidate my scraping functions to ensure that objects are only being populated by a few functions
    - need to cover all scenarios. there are different api calls to get Auction data, for example
3. need to get field names consistent
    - have field names in my classes be what I want them to be everywhere
    - once we get to a populated object, we're done changing things

'''

