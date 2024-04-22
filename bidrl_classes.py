# This file defines all of our classes. Concepts like Item and Invoice which will act as components in our data structures
# Invoice holds a list of Item class instances


# define Item class to hold all of our information about a given item
class Item:
    def __init__(self, id='', description='', tax_rate='', amount='', link='', total_cost='', cost_split=''):
        self.id = id
        self.description = description
        self.tax_rate = tax_rate
        self.amount = amount
        self.link = link
        self.total_cost = total_cost
        self.cost_split = cost_split

    def display(self):
        print(f"ID: {self.id}, Description: {self.description}, Tax Rate: {self.tax_rate}, Amount: {self.amount}, Link: {self.link}, Total Cost: {self.total_cost}, Cost Split: {self.cost_split}")


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

