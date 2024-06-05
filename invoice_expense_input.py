'''
This script is made specifically for myself, the creator of this project.
It helps me input all of my invoices from bidrl into a google form that I use to track my expenses.
It scrapes all the invoices from my account and then asks for some user input, like who in my household bought the item, etc.
It then spits out a list of custom pre-filled links to my google form for easy two-click entry of each invoice into my spreadsheet.
Feel free to use this as an example for invoice processing!

To set up:
- Add a line to config.py with the base of our google form link (minus the pre-filled stuff at the end), named google_form_link_base
    - example line in config.py:
    google_form_link_base = 'https://docs.google.com/forms/d/e/1AAIpBoR6sk3A0HHh-2oDtTA6D_1PmsMQIfG7pWtG8g/viewform?usp=pp_url'
'''


import os, sys, getpass, time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from config import user_email, user_password, google_form_link_base
from datetime import datetime
import bidrl_functions as bf
from bidrl_classes import Item, Invoice


# show the user each item and answer: should item be paid for by [N]ick, [B]ry, or [T]ogether
def user_decide_item_cost_split(invoices):
    for invoice in invoices:
        print(f"\nnew invoice: {invoice.id}")
        for item in invoice.items:
            print(f'\n{item.description} - ${round(float(item.current_bid), 2)} - {invoice.date}') # print: bid amount - item description - date
            print(f'Link: {item.url}')
            cost_split_response = input("Who bought this item? [n]ick, [b]ry, or [t]ogether: ")
            item.cost_split = cost_split_response


# generate google form expense input link for each invoice. populates invoice.expense_input_form_link for each invoice in invoices list
def generate_expense_input_form_links(invoices):
    for invoice in invoices:
        # add up nick cost, bry cost, and together costs
        invoice_cost_nick = 0
        invoice_cost_bry = 0
        invoice_cost_together = 0
        for item in invoice.items:
            if hasattr(item, 'cost_split'): # unsure if this is necessary. AI put this here
                if item.cost_split == 'n':
                    invoice_cost_nick += item.total_cost
                elif item.cost_split == 'b':
                    invoice_cost_bry += item.total_cost
                elif item.cost_split == 't':
                    invoice_cost_together += item.total_cost

        # parse original date string and format to yyyy-mm-dd to work with google form link
        date_obj = datetime.strptime(invoice.date, '%m/%d/%Y')
        formatted_date = date_obj.strftime('%Y-%m-%d')

        form_total = str(round(invoice.total_cost, 2))
        form_contrib_deduct = str(round(invoice_cost_nick, 2)) if invoice_cost_nick != 0 else ''
        form_other_deduct = str(round(invoice_cost_bry, 2)) if invoice_cost_bry != 0 else ''

        form_link = google_form_link_base + \
                    '&entry.80720402=Nick' + \
                    '&entry.602460887=BIDRL' + \
                    '&entry.2039686003=Income' + \
                    '&entry.1813815173=' + form_total + \
                    '&entry.660494524=' + form_contrib_deduct + \
                    '&entry.1146814579=' + form_other_deduct + \
                    '&entry.673325533=' + formatted_date + \
                    '&entry.573687359=Invoice+' + invoice.id

        invoice.expense_input_form_link = form_link

# get user input to determine when to stop pulling invoices
# returns: date object that indicates the date of the earliest invoice we want to pull
def get_start_date_from_user():
    # get user input to determine when to stop pulling invoices
    print("How far to go back? Please enter a start date for invoice gathering. (ex: 4/16/24)")
    start_date = input("Start date: ")
    try:
        start_date_obj = datetime.strptime(start_date, '%m/%d/%y').date()
    except ValueError:
        print("Error: Invalid date format. Please enter the date in the format 'mm/dd/yy'. Exiting program.")
        quit()
    return start_date_obj

# print out all pre-formed google links for entering expenses along with information about each invoice
# requires: list of invoice objects
def print_expense_input_links(invoices):
    print('\n\n\n\nInvoices: ')
    for invoice in invoices:
        print('\nInvoice #' + invoice.id)
        print('Date: ' + invoice.date)
        print('Link: ' + invoice.link)
        print('Expense Input Form Link: ' + invoice.expense_input_form_link)
        print('Items:')
        for item in invoice.items:
            purchaser = 'purchaser not entered as n, b, or t'
            if item.cost_split == 'n': purchaser = 'Nick'
            elif item.cost_split == 'b': purchaser = 'Bry'
            elif item.cost_split == 't': purchaser = 'Together'
            print('$' + str(round(item.total_cost, 2)) + ' - ' + item.description + ' - ' + purchaser)


# print out all pre-formed google links together so I can input them into todoist as a block
def bulk_print_expense_input_links(invoices):
    print('\n\n\n\nInvoice form links for Todoist copy/paste (same links as above): ')
    for invoice in invoices:
        print(invoice.expense_input_form_link)

def update_invoices_total_cost(invoices):
    for invoice in invoices:
        total_cost = 0
        for item in invoice.items:
            total_cost += item.total_cost
        invoice.total_cost = total_cost

# main driver function for this script
def main():
    earliest_invoice_date = get_start_date_from_user()
    #earliest_invoice_date = datetime.strptime('4/25/24', '%m/%d/%y').date() # for debugging

    # open chrome window and set size and position
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless') # use imported credentials from config.py

    # get list of Invoice objects. goes back only as far as the date contained in start_date_obj
    invoices = bf.get_invoices(browser, earliest_invoice_date)

    # calculate total cost of each invoice
    update_invoices_total_cost(invoices)

    # tear down browser object
    browser.quit()

    # now that we have all of our invoices scraped and post-processed information, have the user decide cost split for each item
    user_decide_item_cost_split(invoices)

    # generate google form expense input link for each invoice
    generate_expense_input_form_links(invoices)

    # print out all pre-formed google links for entering expenses along with information about each invoice
    print_expense_input_links(invoices)

    # print out all pre-formed google links together so I can input them into todoist as a block
    bulk_print_expense_input_links(invoices)
    


main()

