import os, sys, getpass
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from config import user_email, user_password, google_form_link_base
from datetime import datetime
import bidrl_functions as bf
from bidrl_classes import Item, Invoice


# use imported credentials from config.py
user = {'name': user_email, 'pw': user_password}


# get user input to determine when to stop pulling invoices
print("How far to go back? Please enter a start date for invoice gathering. (ex: 4/16/24)")
start_date = input("Start date: ")
try:
    start_date_obj = datetime.strptime(start_date, '%m/%d/%y')
except ValueError:
    print("Error: Invalid date format. Please enter the date in the format 'mm/dd/yy'. Program will now stop.")
    sys.exit()


# open chrome window and set size and position
browser = init_browser()


# load and log in to bidrl
bf.login_try_loop(browser, user)


# go to invoices page, set records per page to 36
bf.load_page_invoices(browser, 36)






# to do
# then make a function that just does invoice scraping and returns the invoice class. maybe put this in bf.py?
# then have this script use that function for the purpose of generating invoice expense input info
















# gather list of invoice links

# gather list of all elements with tag name "tr"
tr_elements = browser.find_elements(By.TAG_NAME, 'tr')
invoice_links = []
for tr in tr_elements[2:]: # each tr element is an invoice row
    td_elements = tr.find_elements(By.TAG_NAME, 'td') # each td element is an cell in the row basically
    if len(td_elements) > 0:
        for td in td_elements:
            # one of these td "cells" is the description and will have an element "a", which contains the link to the invoice.
            # we want to try each cell in the row and, if it contains a link, append it to invoice_links
            # the last cell in the row is the view button, which also contains the "a" element with the href link
            # we skip this one to avoid double adding each link
            try:
                if td.text != 'view':
                    invoice_links.append(td.find_element(By.TAG_NAME, 'a').get_property('href'))
            except: continue




invoices = []  # list to hold instances of the Invoice class

for link in invoice_links:
    print("going to: " + link)
    browser.get(link) # go to invoice link
    time.sleep(0.5)

    # information we want to extract for current invoice
    invoice_date = ''
    invoice_num = ''
    invoice_items = []  # This will hold instances of the Item class

    # gather list of all elements with tag name "tr"
    # sometimes no tr elements are found. I don't know why. but if that's the case, keep reloading the page and trying again
    # time out after 5 tries
    tr_elements = browser.find_elements(By.TAG_NAME, 'tr')
    timeout = 0
    while len(tr_elements) == 0 and timeout <= 5:
        print('no tr elements found. reloading')
        browser.get(link)
        time.sleep(0.5)
        tr_elements = browser.find_elements(By.TAG_NAME, 'tr')
        timeout += 1

    # iterate through gathered tr elements to extract information
    for tr in tr_elements: # each tr element is an item row

        # split up text, search through it to find "Date: " and "Invoice: " and extract date and invoice num if found
        for line in tr.text.split('\n'):
            if "Date: " in line:
                invoice_date = line.split("Date: ")[1]
            if "Invoice: " in line:
                invoice_num = line.split("Invoice: ")[1]

        # Initialize an empty dictionary to temporarily hold item details
        temp_item_dict = {'id': '', 'description': '', 'tax_rate': '', 'amount': '', 'link': ''}

        # get all td elements in row, then iterate through. these are the Lot and Description columns, and where we'll find the item link
        td_elements = tr.find_elements(By.TAG_NAME, 'td')
        if len(td_elements) == 2:
            temp_item_dict['id'] = td_elements[0].text
            temp_item_dict['description'] = td_elements[1].text
            try:
                temp_item_dict['link'] = td_elements[1].find_element(By.TAG_NAME, 'a').get_property('href')
            except:
                continue

        # get all th elements in row, then iterate through. these are the Tax Rate and Amount columns
        th_elements = tr.find_elements(By.TAG_NAME, 'th')
        if len(th_elements) == 2:
            temp_item_dict['tax_rate'] = th_elements[0].text
            temp_item_dict['amount'] = th_elements[1].text

        # add scraped item if description is populated and the first value scraped isn't 'Print View'. this trashes the first garbage "item" scraped
        if temp_item_dict['description'] and temp_item_dict['id'] != 'Print View':
            #print(temp_item_dict)
            invoice_items.append(Item(**temp_item_dict))

    print('invoice date: ' + invoice_date)
    try:
        invoice_date_obj = datetime.strptime(invoice_date, '%m/%d/%Y')
        if invoice_date_obj < start_date_obj:
            print('encountered earlier date. breaking')
            break
    except:
        print('exception. failed to parse read invoice date as date object')
        continue

    # Create an Invoice instance and add it to the invoices list
    new_invoice = Invoice(id=invoice_num, date=invoice_date, link=link, items=invoice_items)
    invoices.append(new_invoice)



# now that we have all information about our invoices, do the following:
    # calculate total cost of each invoice
    # show the user each item and have them make decisions for each
        # currently, we just have the user input whether the item should be paid for by [N]ick, [B]ry, or [T]ogether
for invoice in invoices:
    invoice_total_cost = 0
    for item in invoice.items:
        taxed_amount = float(item.tax_rate[-4:]) # last 4 characters of string in Tax Rate field, converted to float
        total_cost_of_item = taxed_amount + float(item.amount)
        invoice_total_cost += total_cost_of_item
        item.total_cost = total_cost_of_item

    # Assuming Invoice class has a method or attribute for storing total cost
    invoice.total_cost = invoice_total_cost

    # prompt user input for cost splitting
    print(f"\nnew invoice: {invoice.id}")
    for item in invoice.items:
        print(f'\n{item.description} - ${round(float(item.amount), 2)} - {invoice.date}') # print: bid amount - item description - date
        print(f'Link: {item.link}')
        cost_split_response = input("Who bought this item? [n]ick, [b]ry, or [t]ogether: ")
        item.cost_split = cost_split_response



# generate google form expense input link for each invoice. populates invoice.expense_input_form_link
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




# print out all pre-formed google links for entering expenses along with information about each invoice
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
print('\n\n\n\nInvoice form links for Todoist copy/paste (same links as above): ')
for invoice in invoices:
    print(invoice.expense_input_form_link)




# add input line here to pause the program so I can look at the browser window it has pulled up
#input()
