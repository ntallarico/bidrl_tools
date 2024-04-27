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


#def get_invoice_data():
    '''
    var invoicesData = [{"id":"3301997","auction_group_id":"152705","bidder":"168516","number_emails_sent":"2","premium_rate":"13","auction_title":"Oversize &#38; Furniture Auction - 161 Johns Rd. Unit A -South Carolina - April 26","relisting_fee":null,"amount_paid":"598.0000000","amount_paid_actual":"5.980","shipment_total":0,"sub_total":5,"adjustments":"0.00","fee_total":"0.00","fee_tax":"0.00","invoice_total":"5.98","effective_premium":"13","premium":"0.65","total_tax":"0.33","title":"Auction Invoice for: Oversize &#38; Furniture Auction - 161 Johns Rd. Unit A -South Carolina - April 26","affiliate_id":"47","item_count":"3","picked_up":"0","relisting_fees":null,"auction_buyer_premium":"13.000","cc_not_needed":"0","picked_up_count":"0","refund":"0.000000","effective_tax":5.841,"tax":0.33,"total":5.98,"balance":0,"init_balance":0,"discounted_total":5.98,"paid":true},{"id":"3300862","auction_group_id":"152707","bidder":"168516","number_emails_sent":"2","premium_rate":"13","auction_title":"Baby Auction - 161 Johns Rd. Unit A -South Carolina - April 26","relisting_fee":null,"amount_paid":"867.0000000","amount_paid_actual":"8.670","shipment_total":0,"sub_total":7.25,"adjustments":"0.00","fee_total":"0.00","fee_tax":"0.00","invoice_total":"8.67","effective_premium":"13","premium":"0.94","total_tax":"0.48","title":"Auction Invoice for: Baby Auction - 161 Johns Rd. Unit A -South Carolina - April 26","affiliate_id":"47","item_count":"5","picked_up":"0","relisting_fees":null,"auction_buyer_premium":"13.000","cc_not_needed":"0","picked_up_count":"0","refund":"0.000000","effective_tax":5.861,"tax":0.48,"total":8.67,"balance":0,"init_balance":0,"discounted_total":8.67,"paid":true},{"id":"3296379","auction_group_id":"152770","bidder":"168516","number_emails_sent":"2","premium_rate":"13","auction_title":"Outdoor Sports Auction - 161 Johns Rd. Unit A -South Carolina - April 25","relisting_fee":null,"amount_paid":"210.0000000","amount_paid_actual":"2.100","shipment_total":0,"sub_total":1.75,"adjustments":"0.00","fee_total":"0.00","fee_tax":"0.00","invoice_total":"2.10","effective_premium":"13","premium":"0.23","total_tax":"0.12","title":"Auction Invoice for: Outdoor Sports Auction - 161 Johns Rd. Unit A -South Carolina - April 25","affiliate_id":"47","item_count":"1","picked_up":"0","relisting_fees":null,"auction_buyer_premium":"13.000","cc_not_needed":"0","picked_up_count":"0","refund":"0.000000","effective_tax":6.061,"tax":0.12,"total":2.1,"balance":0,"init_balance":0,"discounted_total":2.1,"paid":true},{"id":"3292960","auction_group_id":"152767","bidder":"168516","number_emails_sent":"3","premium_rate":"13","auction_title":"Personal Care | Health &#38; Beauty Auction - 161 Johns Rd. Unit A -South Carolina - April 24","relisting_fee":null,"amount_paid":"240.0000000","amount_paid_actual":"2.400","shipment_total":0,"sub_total":2,"adjustments":"0.00","fee_total":"0.00","fee_tax":"0.00","invoice_total":"2.40","effective_premium":"13","premium":"0.26","total_tax":"0.14","title":"Auction Invoice for: Personal Care | Health &#38; Beauty Auction - 161 Johns Rd. Unit A -South Carolina - April 24","affiliate_id":"47","item_count":"1","picked_up":"0","relisting_fees":null,"auction_buyer_premium":"13.000","cc_not_needed":"0","picked_up_count":"0","refund":"0.000000","effective_tax":6.195,"tax":0.14,"total":2.4,"balance":0,"init_balance":0,"discounted_total":2.4,"paid":true},{"id":"3289001","auction_group_id":"152426","bidder":"168516","number_emails_sent":"3","premium_rate":"13","auction_title":"High End Auction - 161 Johns Rd. Unit A -South Carolina - April 21","relisting_fee":null,"amount_paid":"778.0000000","amount_paid_actual":"7.780","shipment_total":0,"sub_total":6.5,"adjustments":"0.00","fee_total":"0.00","fee_tax":"0.00","invoice_total":"7.78","effective_premium":"13","premium":"0.84","total_tax":"0.44","title":"Auction Invoice for: High End Auction - 161 Johns Rd. Unit A -South Carolina - April 21","affiliate_id":"47","item_count":"2","picked_up":"0","relisting_fees":null,"auction_buyer_premium":"13.000","cc_not_needed":"0","picked_up_count":"0","refund":"0.000000","effective_tax":5.995,"tax":0.44,"total":7.78,"balance":0,"init_balance":0,"discounted_total":7.78,"paid":true},{"id":"3288544","auction_group_id":"152280","bidder":"168516","number_emails_sent":"3","premium_rate":"13","auction_title":"Small Furniture &#38; Home Goods Auction - 161 Johns Rd. Unit A -South Carolina - April 20 *ITEMS ADDED*","relisting_fee":null,"amount_paid":"956.0000000","amount_paid_actual":"9.560","shipment_total":0,"sub_total":8,"adjustments":"0.00","fee_total":"0.00","fee_tax":"0.00","invoice_total":"9.56","effective_premium":"13","premium":"1.03","total_tax":"0.53","title":"Auction Invoice for: Small Furniture &#38; Home Goods Auction - 161 Johns Rd. Unit A -South Carolina - April 20 *ITEMS ADDED*","affiliate_id":"47","item_count":"7","picked_up":"0","relisting_fees":null,"auction_buyer_premium":"13.000","cc_not_needed":"0","picked_up_count":"0","refund":"0.000000","effective_tax":5.869,"tax":0.53,"total":9.56,"balance":0,"init_balance":0,"discounted_total":9.56,"paid":true},{"id":"3287653","auction_group_id":"152279","bidder":"168516","number_emails_sent":"3","premium_rate":"13","auction_title":"Oversize &#38; Furniture Auction - 161 Johns Rd. Unit A -South Carolina - April 19","relisting_fee":null,"amount_paid":"180.0000000","amount_paid_actual":"1.800","shipment_total":0,"sub_total":1.5,"adjustments":"0.00","fee_total":"0.00","fee_tax":"0.00","invoice_total":"1.80","effective_premium":"13","premium":"0.20","total_tax":"0.10","title":"Auction Invoice for: Oversize &#38; Furniture Auction - 161 Johns Rd. Unit A -South Carolina - April 19","affiliate_id":"47","item_count":"1","picked_up":"0","relisting_fees":null,"auction_buyer_premium":"13.000","cc_not_needed":"0","picked_up_count":"0","refund":"0.000000","effective_tax":5.882,"tax":0.1,"total":1.8,"balance":0,"init_balance":0,"discounted_total":1.8,"paid":true},{"id":"3286793","auction_group_id":"152282","bidder":"168516","number_emails_sent":"1","premium_rate":"13","auction_title":"Baby Auction - 161 Johns Rd. Unit A -South Carolina - April 19 *ITEMS ADDED*","relisting_fee":null,"amount_paid":"149.0000000","amount_paid_actual":"1.490","shipment_total":0,"sub_total":1.25,"adjustments":"0.00","fee_total":"0.00","fee_tax":"0.00","invoice_total":"1.49","effective_premium":"13","premium":"0.16","total_tax":"0.08","title":"Auction Invoice for: Baby Auction - 161 Johns Rd. Unit A -South Carolina - April 19 *ITEMS ADDED*","affiliate_id":"47","item_count":"1","picked_up":"1","relisting_fees":null,"auction_buyer_premium":"13.000","cc_not_needed":"0","picked_up_count":"1","refund":"0.000000","effective_tax":5.674,"tax":0.08,"total":1.49,"balance":0,"init_balance":0,"discounted_total":1.49,"paid":true},{"id":"3282567","auction_group_id":"152367","bidder":"168516","number_emails_sent":"2","premium_rate":"13","auction_title":"Men Women &#38; Kids Clothing Auction - 161 Johns Rd. Unit A -South Carolina - April 18","relisting_fee":null,"amount_paid":"120.0000000","amount_paid_actual":"1.200","shipment_total":0,"sub_total":1,"adjustments":"0.00","fee_total":"0.00","fee_tax":"0.00","invoice_total":"1.20","effective_premium":"13","premium":"0.13","total_tax":"0.07","title":"Auction Invoice for: Men Women &#38; Kids Clothing Auction - 161 Johns Rd. Unit A -South Carolina - April 18","affiliate_id":"47","item_count":"1","picked_up":"1","relisting_fees":null,"auction_buyer_premium":"13.000","cc_not_needed":"0","picked_up_count":"1","refund":"0.000000","effective_tax":6.195,"tax":0.07,"total":1.2,"balance":0,"init_balance":0,"discounted_total":1.2,"paid":true},{"id":"3281786","auction_group_id":"152281","bidder":"168516","number_emails_sent":"2","premium_rate":"13","auction_title":"Kitchen Goods Auction - 161 Johns Rd. Unit A -South Carolina - April 18","relisting_fee":null,"amount_paid":"868.0000000","amount_paid_actual":"8.680","shipment_total":0,"sub_total":7.25,"adjustments":"0.00","fee_total":"0.00","fee_tax":"0.00","invoice_total":"8.68","effective_premium":"13","premium":"0.94","total_tax":"0.49","title":"Auction Invoice for: Kitchen Goods Auction - 161 Johns Rd. Unit A -South Carolina - April 18","affiliate_id":"47","item_count":"2","picked_up":"1","relisting_fees":null,"auction_buyer_premium":"13.000","cc_not_needed":"0","picked_up_count":"2","refund":"0.000000","effective_tax":5.983,"tax":0.49,"total":8.68,"balance":0,"init_balance":0,"discounted_total":8.68,"paid":true},{"id":"3278882","auction_group_id":"152366","bidder":"168516","number_emails_sent":"3","premium_rate":"13","auction_title":"Auto\/Tool Auction - 161 Johns Rd. Unit A -South Carolina - April 17","relisting_fee":null,"amount_paid":"719.0000000","amount_paid_actual":"7.190","shipment_total":0,"sub_total":6,"adjustments":"0.00","fee_total":"0.00","fee_tax":"0.00","invoice_total":"7.19","effective_premium":"13","premium":"0.78","total_tax":"0.41","title":"Auction Invoice for: Auto\/Tool Auction - 161 Johns Rd. Unit A -South Carolina - April 17","affiliate_id":"47","item_count":"3","picked_up":"1","relisting_fees":null,"auction_buyer_premium":"13.000","cc_not_needed":"0","picked_up_count":"3","refund":"0.000000","effective_tax":6.047,"tax":0.41,"total":7.19,"balance":0,"init_balance":0,"discounted_total":7.19,"paid":true},{"id":"3278412","auction_group_id":"152278","bidder":"168516","number_emails_sent":"3","premium_rate":"13","auction_title":"Personal Care | Health &#38; Beauty Auction - 161 Johns Rd. Unit A -South Carolina - April 17","relisting_fee":null,"amount_paid":"1442.0000000","amount_paid_actual":"14.420","shipment_total":0,"sub_total":12.04,"adjustments":"0.00","fee_total":"0.00","fee_tax":"0.00","invoice_total":"14.42","effective_premium":"13","premium":"1.57","total_tax":"0.81","title":"Auction Invoice for: Personal Care | Health &#38; Beauty Auction - 161 Johns Rd. Unit A -South Carolina - April 17","affiliate_id":"47","item_count":"5","picked_up":"1","relisting_fees":null,"auction_buyer_premium":"13.000","cc_not_needed":"0","picked_up_count":"5","refund":"0.000000","effective_tax":5.952,"tax":0.81,"total":14.42,"balance":0,"init_balance":0,"discounted_total":14.42,"paid":true}]
    '''


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
