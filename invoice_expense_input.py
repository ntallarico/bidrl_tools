import os, sys, getpass, time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from config import user_email, user_password, google_form_link_base
from datetime import datetime
import bidrl_functions as bf
from bidrl_classes import Item, Invoice


# gathers list of invoice links
# requires: web driver object that has pulled up and successfully logged in to bidrl.com
# returns: list of invoice links from logged in account
def scrape_invoice_links(browser):
    # go to invoices page, set records per page to 36
    bf.load_page_invoices(browser, 36)

    tr_elements = browser.find_elements(By.TAG_NAME, 'tr') # gather list of all elements with tag name "tr"

    bf.wait_for_element_by_ID(browser, 'list-form')

    invoice_links = [] # list of invoice links to be returned at the end
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
    
    return invoice_links





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


# main driver function for this script
def main():
    # get user input to determine when to stop pulling invoices
    print("How far to go back? Please enter a start date for invoice gathering. (ex: 4/16/24)")
    #start_date = input("Start date: ")
    start_date = '4/25/24' # for debugging. switch this out with above line
    try:
        start_date_obj = datetime.strptime(start_date, '%m/%d/%y')
    except ValueError:
        print("Error: Invalid date format. Please enter the date in the format 'mm/dd/yy'. Program will now stop.")
        sys.exit()

    # open chrome window and set size and position
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless') # use imported credentials from config.py

    # gather list of invoice links
    invoice_links = scrape_invoice_links(browser)

    # go through list of invoice links and generate a list of Invoice objects, each containing all the information from each invoice linked
    # goes back only as far as the date contained in start_date_obj
    invoices = bf.scrape_invoices(browser, invoice_links, start_date_obj)

    # calculate total cost of each invoice and item
    bf.caculate_total_cost_of_invoices(invoices)

    #browser.close() # closes the browser active window.
    #browser.quit() # closes all browser windows and ends driver's session/process.

    # now that we have all of our invoices scraped and post-processed information, have the user decide cost split for each item
    user_decide_item_cost_split(invoices)

    # generate google form expense input link for each invoice
    generate_expense_input_form_links(invoices)

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

    browser.quit()


main()
