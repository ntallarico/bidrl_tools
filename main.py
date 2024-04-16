import os, sys, getpass
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from config import user_email, user_password, google_form_link_base
from datetime import datetime

# Use imported credentials from config.py
user = {'name': user_email, 'pw': user_password}


# get user input to determine when to stop pulling invoices
print("How far to go back? Please enter a start date for invoice gathering. (ex: 4/16/24)")
start_date = input("Start date: ")
try:
    start_date_obj = datetime.strptime(start_date, '%m/%d/%y')
except ValueError:
    print("Error: Invalid date format. Please enter the date in the format 'mm/dd/yy'. Program will now stop.")
    sys.exit()


browser = webdriver.Chrome()
browser.get('https://www.bidrl.com/login')
browser.set_window_position(0, 0)
browser.maximize_window()
time.sleep(0.5)
userName = browser.find_element(By.NAME, 'username')
password = browser.find_element(By.NAME, 'password')

#put all elements with tag name "button" into a list
button_elements = browser.find_elements(By.TAG_NAME, 'button')
#find the first element in the button_elements list with text 'LOGIN'
login_button = next(obj for obj in button_elements if obj.text == 'LOGIN')


actions = ActionChains(browser)
actions.move_to_element(userName).send_keys(user['name'])
actions.send_keys(Keys.TAB).send_keys(user['pw'])
actions.move_to_element(login_button).click()
actions.perform()



#go to invoices page, set records per page to 36
time.sleep(1)
browser.get('https://www.bidrl.com/myaccount/invoices')
perpage = browser.find_element(By.ID, 'perpage-top')
actions = ActionChains(browser)
actions.move_to_element(perpage).click()
actions.send_keys("3")
actions.send_keys(Keys.ENTER)
actions.perform()


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


'''# for dev. delete this and replace with commented out section above
invoice_links = ['https://www.bidrl.com/myaccount/invoice/invid/3273850', 'https://www.bidrl.com/myaccount/invoice/invid/3275732']''' 

#print(invoice_links)

# now that we have our array of links, go into each one and extract the necessary information we need
invoices = [] # list including all information about our scraped invoices. invoice num, date, link, and lists of info about the items
for link in invoice_links:
    print("going to: " + link)
    browser.get(link) # go to invoice link
    time.sleep(0.5)

    # information we want to extract for current invoice
    invoice_date = ''
    invoice_num = ''
    invoice_items = [] # list of lists, each containing 5 cells: Lot, Description, Tax Rate, Amount, and item link
    
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
        #print(tr.text)

        # split up text, search through it to find "Date: " and extract invoice date if found
        for line in tr.text.split('\n'): # Split the text by lines and iterate through each line
            if "Date: " in line:
                invoice_date = line.split("Date: ")[1] # Split the line by "Date: " and take the second element

        #print('invoice date: ' + invoice_date)

        # split up text, search through it to find "Invoice: " and extract invoice number if found
        for line in tr.text.split('\n'):
            if "Invoice: " in line:
                invoice_num = line.split("Invoice: ")[1]

        invoice_item = [] # list that will be appended to invoice_items. contains 5 cells: Lot, Description, Tax Rate, Amount, and item link

        item_link = ''

         # get all td elements in row, then iterate through. these are the Lot and Description columns, and where we'll find the item link
        td_elements = tr.find_elements(By.TAG_NAME, 'td')
        if len(td_elements) == 2:
            for td in td_elements:
                invoice_item.append(td.text)
            # both of these td elements with have an element "a", which contains a link to the item
            # both links are the same, so the fact that we're setting the variable on both doesn't matter
            try: # try each cell in the row and, if it contains a link, set item_link to the text
                item_link = td.find_element(By.TAG_NAME, 'a').get_property('href')
            except: continue

        # get all th elements in row, then iterate through. these are the Tax Rate and Amount columns
        th_elements = tr.find_elements(By.TAG_NAME, 'th')
        if len(th_elements) == 2:
            for th in th_elements:
                invoice_item.append(th.text)

        invoice_item.append(item_link)

        # if the invoice_item list is an actual invoice item list and not text from some of the other elements on the page, add it to invoice_items
        if len(invoice_item) == 5 and invoice_item[0] != 'Lot':
            invoice_items.append(invoice_item)

    print('invoice date: ' + invoice_date)
    try:
        invoice_date_obj = datetime.strptime(invoice_date, '%m/%d/%Y')
        if invoice_date_obj < start_date_obj:
            print('encountered earlier date. breaking')
            break
    except:
        print('exception. failed to parse read invoice date as date object')
        continue

    # create an entry in invoices
    invoices_entry = []
    invoices_entry.append(invoice_num)
    invoices_entry.append(invoice_date)
    invoices_entry.append(link)
    invoices_entry.append(invoice_items)
    invoices.append(invoices_entry)
    #print(invoices_entry)



# iterate through invoices list and append additional information
# invoices[x][4] = total cost of invoice
for invoice in invoices:
    # append total cost of the invoice
    invoice_total_cost = 0
    for item in invoice[3]:
        taxed_amount = item[2][-4:] # last 4 characters of Tax Rate column
        total_cost_of_item = float(taxed_amount) + (float(item[3]) * 1.13)
        invoice_total_cost += total_cost_of_item
        item.append(total_cost_of_item) # add total cost of item to the item list

    invoice.append(invoice_total_cost)


# now that we have all information about our invoices, show the user each item and have them make decisions for each
# we append these decisions to the end of each item info list contained within each invoice
# currently, we just have the user input whether the item should be paid for by [N]ick, [B]ry, or [T]ogether
for invoice in invoices:
    print("\nnew invoice: " + invoice[0])
    for item in invoice[3]:
        print('')
        print(item[1] + ' - $' + str(round(float(item[3]), 2)) + ' - ' + invoice[1] ) # print bid amount and item description
        print('Link: ' + item[4])
        cost_split_response = input("Who bought this item? [n]ick, [b]ry, or [t]ogether: ")
        item.append(cost_split_response)


# iterate through invoices list and append additional information
# invoices[x][5] = pre-filled google form link to submit expense input for invoice
for invoice in invoices:
    # add up nick cost, bry cost, and together costs
    invoice_cost_nick = 0
    invoice_cost_bry = 0
    invoice_cost_together = 0
    for item in invoice[3]:
        #print("new item" + item[1])
        if item[6] == 'n': invoice_cost_nick += item[5]
        if item[6] == 'b': invoice_cost_bry += item[5]
        if item[6] == 't': invoice_cost_together += item[5]
    '''print(invoice_cost_nick)
    print(invoice_cost_bry)
    print(invoice_cost_together)'''


    # parse original date string and format to yyyy-mm-dd to work with google form link
    date_obj = datetime.strptime(invoice[1], '%m/%d/%Y')
    formatted_date = date_obj.strftime('%Y-%m-%d')

    form_total = str(round(invoice[4], 2))
    form_contrib_deduct = str(round(invoice_cost_nick, 2)) if invoice_cost_nick != 0 else ''
    form_other_deduct = str(round(invoice_cost_bry, 2)) if invoice_cost_bry != 0 else ''

    form_link = google_form_link_base
    form_link = form_link + '&entry.80720402=' + 'Nick' # Contributor
    form_link = form_link + '&entry.602460887=' + 'BIDRL' # Category
    form_link = form_link + '&entry.2039686003=' + 'Income' # Split
    form_link = form_link + '&entry.1813815173=' + form_total # Total
    form_link = form_link + '&entry.660494524=' + form_contrib_deduct # Contributor Deduction
    form_link = form_link + '&entry.1146814579=' + form_other_deduct # Other Deduction
    form_link = form_link + '&entry.673325533=' + formatted_date # Date
    form_link = form_link + '&entry.573687359=' + 'Invoice+' + invoice[0] # Notes

    invoice.append(form_link)


# print out all pre-formed google links for entering expenses along with information about each invoice
print('\n\n\n\nInvoices: ')
for invoice in invoices:
    print('\nInvoice #' + invoice[0])
    print('Date: ' + invoice[1])
    print('Link: ' + invoice[2])
    print('Expense Input Form Link: ' + invoice[5])
    print('Items:')
    for item in invoice[3]:
        purchaser = ''
        if item[6] == 'n': purchaser = 'Nick'
        elif item[6] == 'b': purchaser = 'Bry'
        elif item[6] == 't': purchaser = 'Together'
        print('$' + str(round(item[5], 2)) + ' - ' + item[1] + ' - ' + purchaser)


# print out all pre-formed google links together so I can input them into todoist as a block
print('\n\n\n\nInvoice form links for Todoist copy/paste (same links as above): ')
for invoice in invoices:
    print(invoice[5])




# add input line here to pause the program so I can look at the browser window it has pulled up
#input()
