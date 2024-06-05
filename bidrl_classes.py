# This file defines all of our classes. Concepts like Item and Invoice which will act as components in our data structures
# These object structures ensure a standard for each concept across all of our functions and files
# web scraping functions will be responsible for processing scraped data into the correct types/formats for these objects
# once the object is returned, the data should be good to go and consistent going forward


# define Bid class to hold all of our information about a given bid
class Bid:
    def __init__(self
                 , bid_id: str = None
                 , item_id: str = None
                 , user_name: str = None
                 , bid: float = None
                 , bid_time: str = None
                 , time_of_bid: str = None
                 , time_of_bid_unix: int = None
                 , buyer_number: str = None
                 , description: str = None):
        if bid_id is not None and not isinstance(bid_id, str):
            raise TypeError(f"Expected bid_id to be str, got {type(bid_id).__name__}")
        if item_id is not None and not isinstance(item_id, str):
            raise TypeError(f"Expected item_id to be str, got {type(item_id).__name__}")
        if user_name is not None and not isinstance(user_name, str):
            raise TypeError(f"Expected user_name to be str, got {type(user_name).__name__}")
        if bid is not None and not isinstance(bid, float):
            raise TypeError(f"Expected bid to be float, got {type(bid).__name__}")
        if bid_time is not None and not isinstance(bid_time, str):
            raise TypeError(f"Expected bid_time to be str, got {type(bid_time).__name__}")
        if time_of_bid is not None and not isinstance(time_of_bid, str):
            raise TypeError(f"Expected time_of_bid to be str, got {type(time_of_bid).__name__}")
        if time_of_bid_unix is not None and not isinstance(time_of_bid_unix, int):
            raise TypeError(f"Expected time_of_bid_unix to be int, got {type(time_of_bid_unix).__name__}")
        if buyer_number is not None and not isinstance(buyer_number, str):
            raise TypeError(f"Expected buyer_number to be str, got {type(buyer_number).__name__}")
        if description is not None and not isinstance(description, str):
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
        
# define Item class to hold all of our information about a given item
# Item class will contain a list of Bid classes
class Item:
    def __init__(self
                 , id: str = None
                 , auction_id: str = None
                 , description: str = None
                 , tax_rate: float = None
                 , buyer_premium: float = None
                 , current_bid: float = None
                 , url: str = None
                 , highbidder_username: str = None
                 , lot_number: str = None
                 , bidding_status: str = None
                 , end_time_unix: int = None
                 , bids: list = None # holds a list of Bid objects
                 , is_favorite: int = None
                 , bid_count: int = None
                 , viewed: int = None
                 , images: list = None # holds a list of Image objects
                 , total_cost: float = None
                 , cost_split: str = None
                 , max_desired_bid: float = None
                 , item_bid_group_id: str = None):  # used to specify which items belong to a set that we only intend to win 1 of
        if id is not None and not isinstance(id, str):
            raise TypeError(f"Expected id to be str, got {type(id).__name__}")
        if auction_id is not None and not isinstance(auction_id, str):
            raise TypeError(f"Expected auction_id to be str, got {type(auction_id).__name__}")
        if description is not None and not isinstance(description, str):
            raise TypeError(f"Expected description to be str, got {type(description).__name__}")
        if tax_rate is not None and not isinstance(tax_rate, float):
            raise TypeError(f"Expected tax_rate to be float, got {type(tax_rate).__name__}")
        if buyer_premium is not None and not isinstance(buyer_premium, float):
            raise TypeError(f"Expected buyer_premium to be float, got {type(buyer_premium).__name__}")
        if current_bid is not None and not isinstance(current_bid, float):
            raise TypeError(f"Expected current_bid to be float, got {type(current_bid).__name__}")
        if url is not None and not isinstance(url, str):
            raise TypeError(f"Expected url to be str, got {type(url).__name__}")
        if highbidder_username is not None and not isinstance(highbidder_username, str):
            raise TypeError(f"Expected highbidder_username to be str, got {type(highbidder_username).__name__}")
        if lot_number is not None and not isinstance(lot_number, str):
            raise TypeError(f"Expected lot_number to be str, got {type(lot_number).__name__}")
        if bidding_status is not None and not isinstance(bidding_status, str):
            raise TypeError(f"Expected bidding_status to be str, got {type(bidding_status).__name__}")
        if end_time_unix is not None and not isinstance(end_time_unix, int):
            raise TypeError(f"Expected end_time_unix to be int, got {type(end_time_unix).__name__}")
        if bids is not None and not all(isinstance(bid, Bid) for bid in bids):
            raise TypeError("All elements in bids must be instances of Bid")
        if is_favorite is not None and not isinstance(is_favorite, int):
            raise TypeError(f"Expected is_favorite to be int, got {type(is_favorite).__name__}")
        if bid_count is not None and not isinstance(bid_count, int):
            raise TypeError(f"Expected bid_count to be int, got {type(bid_count).__name__}")
        if viewed is not None and not isinstance(viewed, int):
            raise TypeError(f"Expected viewed to be int, got {type(viewed).__name__}")
        if images is not None and not all(isinstance(image, Image) for image in images):
            raise TypeError("All elements in images must be instances of Image")
        if total_cost is not None and not isinstance(total_cost, float):
            raise TypeError(f"Expected total_cost to be float, got {type(total_cost).__name__}")
        if cost_split is not None and not isinstance(cost_split, str):
            raise TypeError(f"Expected cost_split to be str, got {type(cost_split).__name__}")
        if max_desired_bid is not None and not isinstance(max_desired_bid, float):
            raise TypeError(f"Expected max_desired_bid to be float, got {type(max_desired_bid).__name__}")
        if item_bid_group_id is not None and not isinstance(item_bid_group_id, str):
            raise TypeError(f"Expected item_bid_group_id to be str, got {type(item_bid_group_id).__name__}")

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
        self.images = images if images is not None else []
        #self.total_cost = total_cost # calculated total cost based on current_bid, tax rate, and buyer_premium
        self.cost_split = cost_split
        self.max_desired_bid = max_desired_bid
        self.item_bid_group_id = item_bid_group_id

        # populate total_cost based on current_bid, tax_rate, and buyer_premium
        if self.tax_rate is not None and self.buyer_premium is not None and self.current_bid is not None:
            self.total_cost = round(self.tax_rate * (self.current_bid * (1 + self.buyer_premium)), 2) + round(self.current_bid * (1 + self.buyer_premium), 2)

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
        print(f"Item Bid Group ID: {self.item_bid_group_id}")

    def display_bids(self):
        for bid in self.bids:
            bid.display()
    
    def display_images(self):
        for image in self.images:
            image.display()


# define Affiliate class to hold all of our information about a given affiliate
class Affiliate:
    def __init__(self
                 , id: str = None
                 , logo: str = None
                 , do_not_display_tab: int = None
                 , company_name: str = None
                 , firstname: str = None
                 , lastname: str = None
                 , auc_count: int = None):
        if id is not None and not isinstance(id, str):
            raise TypeError(f"Expected id to be str, got {type(id).__name__}")
        if logo is not None and not isinstance(logo, str):
            raise TypeError(f"Expected logo to be str, got {type(logo).__name__}")
        if do_not_display_tab is not None and not isinstance(do_not_display_tab, int):
            raise TypeError(f"Expected do_not_display_tab to be int, got {type(do_not_display_tab).__name__}")
        if company_name is not None and not isinstance(company_name, str):
            raise TypeError(f"Expected company_name to be str, got {type(company_name).__name__}")
        if firstname is not None and not isinstance(firstname, str):
            raise TypeError(f"Expected firstname to be str, got {type(firstname).__name__}")
        if lastname is not None and not isinstance(lastname, str):
            raise TypeError(f"Expected lastname to be str, got {type(lastname).__name__}")
        if auc_count is not None and not isinstance(auc_count, int):
            raise TypeError(f"Expected auc_count to be int, got {type(auc_count).__name__}")

        self.id = id
        self.logo = logo
        self.do_not_display_tab = do_not_display_tab
        self.company_name = company_name
        self.firstname = firstname
        self.lastname = lastname
        self.auc_count = auc_count

    def display(self):
        print(f"ID: {self.id}, Company: {self.company_name}, "
                f"First Name: {self.firstname}, Last Name: {self.lastname}, "
                f"Auction Count: {self.auc_count}")


# define Auction class to hold all of our information about a given auction
# Auction class will contain a list of Item classes
class Auction:
    def __init__(self
                 , id: str = None
                 , url: str = None
                 , items: list = None
                 , title: str = None
                 , item_count: int = None
                 , start_datetime: str = None
                 , status: str = None
                 , affiliate_id: str = None
                 , aff_company_name: str = None
                 , state_abbreviation: str = None
                 , city: str = None
                 , zip: str = None
                 , address: str = None):
        if id is not None and not isinstance(id, str):
            raise TypeError(f"Expected id to be str, got {type(id).__name__}")
        if url is not None and not isinstance(url, str):
            raise TypeError(f"Expected url to be str, got {type(url).__name__}")
        if items is not None and not all(isinstance(item, Item) for item in items):
            raise TypeError("All elements in items must be an instance of Item")
        if title is not None and not isinstance(title, str):
            raise TypeError(f"Expected title to be str, got {type(title).__name__}")
        if item_count is not None and not isinstance(item_count, int):
            raise TypeError(f"Expected item_count to be int, got {type(item_count).__name__}")
        if start_datetime is not None and not isinstance(start_datetime, str):
            raise TypeError(f"Expected start_datetime to be str, got {type(start_datetime).__name__}")
        if status is not None and not isinstance(status, str):
            raise TypeError(f"Expected status to be str, got {type(status).__name__}")
        if affiliate_id is not None and not isinstance(affiliate_id, str):
            raise TypeError(f"Expected affiliate_id to be str, got {type(affiliate_id).__name__}")
        if aff_company_name is not None and not isinstance(aff_company_name, str):
            raise TypeError(f"Expected aff_company_name to be str, got {type(aff_company_name).__name__}")
        if state_abbreviation is not None and not isinstance(state_abbreviation, str):
            raise TypeError(f"Expected state_abbreviation to be str, got {type(state_abbreviation).__name__}")
        if city is not None and not isinstance(city, str):
            raise TypeError(f"Expected city to be str, got {type(city).__name__}")
        if zip is not None and not isinstance(zip, str):
            raise TypeError(f"Expected zip to be str, got {type(zip).__name__}")
        if address is not None and not isinstance(address, str):
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

    def display_items(self):
        print("Items:")
        for item in self.items:
            item.display()


# define Invoice class to hold all of our information about a given invoice
# Invoice class will contain a list of Item classes
class Invoice:
    def __init__(self
                 , id: str = None
                 , date: str = None
                 , link: str = None
                 , items: list = None
                 , total_cost: float = None
                 , expense_input_form_link: str = None):
        if id is not None and not isinstance(id, str):
            raise TypeError(f"Expected id to be str, got {type(id).__name__}")
        if date is not None and not isinstance(date, str):
            raise TypeError(f"Expected date to be str, got {type(date).__name__}")
        if link is not None and not isinstance(link, str):
            raise TypeError(f"Expected link to be str, got {type(link).__name__}")
        if items is not None and not all(isinstance(item, Item) for item in items):
            raise TypeError("All elements in items must be an instance of Item")
        if total_cost is not None and not isinstance(total_cost, (float, int)):  # Accept int for convenience
            raise TypeError(f"Expected total_cost to be float or int, got {type(total_cost).__name__}")
        if expense_input_form_link is not None and not isinstance(expense_input_form_link, str):
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


# define Image class to hold all of our information about a given image
class Image:
    def __init__(self
                 , item_id: str = None
                 , image_url: str = None
                 , image_height: int = None
                 , image_width: int = None):
        if item_id is not None and not isinstance(item_id, str):
            raise TypeError(f"Expected item_id to be str, got {type(item_id).__name__}")
        if image_url is not None and not isinstance(image_url, str):
            raise TypeError(f"Expected image_url to be str, got {type(image_url).__name__}")
        if image_height is not None and not isinstance(image_height, int):
            raise TypeError(f"Expected image_height to be int, got {type(image_height).__name__}")
        if image_width is not None and not isinstance(image_width, int):
            raise TypeError(f"Expected image_width to be int, got {type(image_width).__name__}")

        self.item_id = item_id
        self.image_url = image_url
        self.image_height = image_height
        self.image_width = image_width

    def display(self):
        print(f"Image ID: {self.item_id}, URL: {self.image_url}, Height: {self.image_height}, Width: {self.image_width}")

