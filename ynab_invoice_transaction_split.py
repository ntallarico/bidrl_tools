import requests
import json
from config import user_email, user_password, ynab_api_token, ynab_budget_id, ynab_category_dict
from datetime import datetime, date, timedelta
import bidrl_functions as bf
from bidrl_classes import Item, Invoice
from typing import Union

# reference: https://api.ynab.com/v1#/

class Transaction:
    def __init__(self
                 , id: str = None
                 , date: Union[str, date] = None
                 , amount: float = None
                 , memo: str = None
                 , cleared: str = None
                 , approved: bool = None
                 , flag_color: str = None
                 , account_id: str = None
                 , payee_id: str = None
                 , category_id: str = None
                 , transfer_account_id: str = None
                 , transfer_transaction_id: str = None
                 , matched_transaction_id: str = None
                 , import_id: str = None, deleted: bool = None
                 , account_name: str = None
                 , payee_name: str = None
                 , category_name: str = None
                 , subtransactions: list = None
                 , bidrl_invoice: Invoice = None):
        
        self._check_type('id', id, str)
        self._check_type('date', date, (str, date))
        self._check_type('amount', amount, float)
        self._check_type('memo', memo, str)
        self._check_type('cleared', cleared, str)
        self._check_type('approved', approved, bool)
        self._check_type('flag_color', flag_color, str)
        self._check_type('account_id', account_id, str)
        self._check_type('payee_id', payee_id, str)
        self._check_type('category_id', category_id, str)
        self._check_type('transfer_account_id', transfer_account_id, str)
        self._check_type('transfer_transaction_id', transfer_transaction_id, str)
        self._check_type('matched_transaction_id', matched_transaction_id, str)
        self._check_type('import_id', import_id, str)
        self._check_type('deleted', deleted, bool)
        self._check_type('account_name', account_name, str)
        self._check_type('payee_name', payee_name, str)
        self._check_type('category_name', category_name, str)
        self._check_type('subtransactions', subtransactions, list)
        self._check_type('bidrl_invoice', bidrl_invoice, Invoice)

        self.id = id
        self.date = self._convert_to_date(date)
        self.amount = amount
        self.memo = memo
        self.cleared = cleared
        self.approved = approved
        self.flag_color = flag_color
        self.account_id = account_id
        self.payee_id = payee_id
        self.category_id = category_id
        self.transfer_account_id = transfer_account_id
        self.transfer_transaction_id = transfer_transaction_id
        self.matched_transaction_id = matched_transaction_id
        self.import_id = import_id
        self.deleted = deleted
        self.account_name = account_name
        self.payee_name = payee_name
        self.category_name = category_name
        self.subtransactions = subtransactions
        self.bidrl_invoice = bidrl_invoice

    def _check_type(self, name, value, expected_type):
        if value is not None and not isinstance(value, expected_type):
            raise TypeError(f"Expected {name} to be {expected_type.__name__}, got {type(value).__name__}")

    def _convert_to_date(self, date):
        if isinstance(date, str):
            return datetime.strptime(date, '%Y-%m-%d').date()
        elif isinstance(date, date):
            return date
        else:
            raise TypeError("Expected date to be a string or a date object")

    def display(self):
        print(f"Transaction ID: {self.id}")
        print(f"Date: {self.date}")
        print(f"Amount: {self.amount}")
        print(f"Memo: {self.memo}")
        #print(f"Cleared: {self.cleared}")
        #print(f"Approved: {self.approved}")
        #print(f"Flag Color: {self.flag_color}")
        #print(f"Account ID: {self.account_id}")
        #print(f"Payee ID: {self.payee_id}")
        #print(f"Category ID: {self.category_id}")
        #print(f"Transfer Account ID: {self.transfer_account_id}")
        #print(f"Transfer Transaction ID: {self.transfer_transaction_id}")
        #print(f"Matched Transaction ID: {self.matched_transaction_id}")
        #print(f"Import ID: {self.import_id}")
        #print(f"Deleted: {self.deleted}")
        print(f"Account Name: {self.account_name}")
        print(f"Payee Name: {self.payee_name}")
        print(f"Category Name: {self.category_name}")
        print(f"Subtransactions: {self.subtransactions}")
        if self.bidrl_invoice is None:
            print("BidRL Invoice: None")
        else:
            print(f"BidRL Invoice ID: {self.bidrl_invoice.id}")



"""
Retrieves and prints the YNAB budgets using the YNAB API.

This function sends a GET request to the YNAB API to fetch all budgets
associated with the account. It uses the API token stored in ynab_api_token
for authentication.
"""
def get_ynab_budgets():
    
    # Define the API endpoint and headers
    url = "https://api.ynab.com/v1/budgets"
    headers = {
        "Authorization": "Bearer " + ynab_api_token
    }

    # Make the API request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON content
        content = response.json()
        
        # Pretty print the JSON content
        print(json.dumps(content, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# scrape list of transactions from ynab
# payee is the name of the payee to filter by, categorized is 'all', 'categorized', or 'uncategorized'
def get_ynab_transactions(payee=None, categorized='all'):
    # Define the API endpoint and headers
    url = f"https://api.ynab.com/v1/budgets/{ynab_budget_id}/transactions"
    headers = {
        "Authorization": f"Bearer {ynab_api_token}"
    }

    # Make the API request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON content
        content = response.json()
        
        # Extract transactions from the response
        transactions = content['data']['transactions']
        
        # Create a list to hold Transaction instances
        transactions_list = []

        # Create Transaction instances for the specified payee and categorized status
        for transaction in transactions:
            if (payee is None or transaction['payee_name'] == payee) and \
               (categorized == 'all' or 
                (categorized == 'categorized' and transaction['category_name'] != 'Uncategorized') or 
                (categorized == 'uncategorized' and transaction['category_name'] == 'Uncategorized')):
                
                # Create a Transaction instance
                transaction_instance = Transaction(
                    id=transaction['id'],
                    date=transaction['date'],
                    amount=(transaction['amount'] / -1000),
                    memo=transaction['memo'],
                    cleared=transaction['cleared'],
                    approved=transaction['approved'],
                    flag_color=transaction['flag_color'],
                    account_id=transaction['account_id'],
                    payee_id=transaction['payee_id'],
                    category_id=transaction['category_id'],
                    transfer_account_id=transaction['transfer_account_id'],
                    transfer_transaction_id=transaction['transfer_transaction_id'],
                    matched_transaction_id=transaction['matched_transaction_id'],
                    import_id=transaction['import_id'],
                    deleted=transaction['deleted'],
                    account_name=transaction['account_name'],
                    payee_name=transaction['payee_name'],
                    category_name=transaction['category_name'],
                    subtransactions=transaction['subtransactions']
                )
                
                # Add the instance to the list
                transactions_list.append(transaction_instance)
        
        return transactions_list

    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# get the oldest transaction date, returned as a datetime object
def get_oldest_transaction_date(transactions):
    if not transactions:
        return None
    oldest_transaction = min(transactions, key=lambda x: x.date)
    return oldest_transaction.date

def update_invoices_total_cost(invoices):
    for invoice in invoices:
        total_cost = 0
        for item in invoice.items:
            total_cost += item.total_cost
        invoice.total_cost = round(total_cost, 2)

# fetch cost_split from the database
def fetch_cost_split_from_db(conn, item_id, auction_id):
    cursor = conn.cursor()
    cursor.execute("SELECT cost_split FROM items_user_input WHERE item_id = ? AND auction_id = ?", (item_id, auction_id))
    result = cursor.fetchone()
    return result[0] if result else None

# update item cost_split from the database
def update_item_cost_split_from_db(invoices):
    print("Updating item cost_split from the database.")
    conn = bf.init_sqlite_connection(path = 'local_files/auto_bid/', database = 'bidrl_user_input')
    for invoice in invoices:
        for item in invoice.items:
            cost_split = fetch_cost_split_from_db(conn, item.id, item.auction_id)
            if cost_split:
                item.cost_split = cost_split
            else:
                print(f"cost_split not found for item_id {item.id} and auction_id {item.auction_id}.")
                item.cost_split = 'not_found'
    conn.close()

# takes the dict ynab_category_dict, polls the api for category ids, then returns a new dict with the
# category names replaced with their ids
def get_category_ids_from_ynab_category_dict(ynab_category_dict):
    print("Getting category ids from YNAB category dict.")

    # Define the API endpoint and headers
    url = f"https://api.ynab.com/v1/budgets/{ynab_budget_id}/categories"
    headers = {
        "Authorization": f"Bearer {ynab_api_token}"
    }

    # Make the API request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON content
        content = response.json()
        
        # Extract categories from the response
        categories = content['data']['category_groups']
        
        # Create a mapping of category names to category ids
        category_name_to_id = {}
        for group in categories:
            for category in group['categories']:
                category_name_to_id[category['name']] = category['id']
        
        # Replace category names in the dict with category ids
        updated_dict = {}
        for key, value in ynab_category_dict.items():
            print(f"Searching for category name: {value}")
            if value in category_name_to_id:
                updated_dict[key] = category_name_to_id[value]
                print(f"Found category id: {category_name_to_id[value]} for category name: {value}")
            else:
                updated_dict[key] = None  # or handle the case where the category name is not found
                print(f"Category name: {value} not found")
        
        print("Updated category dict with ids:", updated_dict)
        return updated_dict
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# match transactions an invoices on amount and date, 
# then populate the bidrl_invoice field of the transaction with the matched invoice
# date_match_tolerance is the number of days that the transaction date and invoice date can be different and still be considered a match
# cost_match_tolerance is the amount difference that the transaction amount and invoice total cost can
    # be different and still be considered a match. this is to make up for the case where the total cost
    # is slightly different due to rounding or other slight inaccuracies when calculating the total cost
def match_transactions_to_invoices(transactions
                                   , invoices
                                   , date_match_tolerance = 0
                                   , cost_match_tolerance = 0
                                   , verbose = False):
    if verbose: print("Matching transactions to invoices.")
    
    # maintain a list of matched transaction ids and invoice ids that have been matched,
    # so that we do not match the same transaction or invoice more than once
    matched_transaction_ids = set()
    matched_invoice_ids = set()
    
    for transaction in transactions:
        if transaction.id in matched_transaction_ids:
            continue
        if verbose: print(f"\nAttempting to find match for transaction with amount {transaction.amount} and date {transaction.date}.")
        match_found = False
        for invoice in invoices:
            if invoice.id in matched_invoice_ids:
                continue
            invoice_date = datetime.strptime(invoice.date, '%m/%d/%Y').date() # Convert invoice.date to a date object
            if verbose: print(f"Comparing invoice with total cost {invoice.total_cost} and date {invoice_date}.")
            date_difference = abs((transaction.date - invoice_date).days)
            cost_difference = abs(transaction.amount - invoice.total_cost)
            if cost_difference <= cost_match_tolerance and date_difference <= date_match_tolerance:
                if verbose: print(f"Matched transaction {transaction.id} to invoice {invoice.id}")
                transaction.bidrl_invoice = invoice
                matched_transaction_ids.add(transaction.id)
                matched_invoice_ids.add(invoice.id)
                match_found = True
                break
        if not match_found:
            print(f"No match found for transaction with amount {transaction.amount} and date {transaction.date}.")
            print("Consider adjusting date_match_tolerance or cost_match_tolerance.")
            print("Exiting program.")
            quit()

def get_processed_bidrl_invoices(oldest_transaction_date):
    print(f"\nGetting BidRL invoices from {oldest_transaction_date} to present.")

    if oldest_transaction_date is None:
        print("\nOldest transaction date is None. Exiting program.")
        quit()
    
    # get logged in webdriver instance using imported credentials from config.py
    browser = bf.get_logged_in_webdriver(user_email, user_password, 'headless') # use imported credentials from config.py

    # get list of Invoice objects. goes back only as far as the date contained in start_date_obj
    invoices = bf.get_invoices(browser, oldest_transaction_date)

    # tear down browser object
    browser.quit()

    print(f"\nFound {len(invoices)} invoices. Proceeding to process them.")

    # update total cost of each invoice
    update_invoices_total_cost(invoices)

    # update item cost_split from the database
    update_item_cost_split_from_db(invoices)

    return invoices

# process transaction-invoice matches to determine splits
def split_transactions(transactions):
    print("\nProcessing transaction-invoice matches to determine splits.")

    # get dict mapping our cost_split values to ynab category ids
    category_id_mapping = get_category_ids_from_ynab_category_dict(ynab_category_dict)

    for transaction in transactions:
        if transaction.bidrl_invoice is not None:
            invoice = transaction.bidrl_invoice
            
            splits = []
            # create a running sum of the total costs of the items in an invoice, then adjust the last item's amount
            # to make sure that the sum adds up to the total cost of the transaction
            running_sum_of_total_costs = 0
            for index, item in enumerate(invoice.items):
                if index == len(invoice.items) - 1:
                    split_amount = round(transaction.amount - running_sum_of_total_costs, 2)
                else:
                    split_amount = round(item.total_cost, 2)
                    running_sum_of_total_costs += split_amount
                
                # determine the category id based on the cost_split value and the category_id_mapping
                cost_split_value = item.cost_split
                if cost_split_value in category_id_mapping:
                    category_id = category_id_mapping[cost_split_value]
                else:
                    category_id = None
                    print(f"cost_split value for item {item.id} not found in category_id_mapping. Value: {cost_split_value}")

                memo = f"{item.description}        {item.url}"
                
                split = {
                    'amount': int(split_amount * -1000)
                    #, 'payee_id': ''
                    #, 'payee_name': ''
                    , 'memo': memo
                }
                # only add category_id if it is not None (situations where cost_split is unmapped or not found in db)
                if category_id is not None:
                    split['category_id'] = category_id

                splits.append(split)
                
            transaction.subtransactions = splits
            print(f"\nIdentified {len(splits)} splits for {transaction.id} (amount: {transaction.amount}, date: {transaction.date}).")
            print(f"Splits: {transaction.subtransactions}")
        else:
            print(f"No invoice found for transaction with amount {transaction.amount} and date {transaction.date}.")
            print("Exiting program.")
            quit()

def check_split_transactions(transactions):
    print("\nChecking splits for transactions to ensure they are correct before submitting to YNAB.")
    for transaction in transactions:
        transaction_amount = int(transaction.amount * -1000)
        if transaction.subtransactions:
            print(f"Found {len(transaction.subtransactions)} splits for transaction {transaction.id}. Amount: {transaction.amount}, Date: {transaction.date}.")
        
            # Calculate the sum of all values in 'amount' field in all subtransactions
            subtransactions_sum = sum(subtransaction['amount'] for subtransaction in transaction.subtransactions)
            
            # Compare it to the 'amount' field in the transaction
            if subtransactions_sum != transaction_amount:
                print(f"Mismatch found for transaction {transaction.id}.")
                print(f"Transaction amount: {transaction_amount}")
                print(f"Sum of subtransaction amounts: {subtransactions_sum}")
                print("Exiting program.")
                quit()
            
            print(f"Transaction {transaction.id} with amount {transaction.amount} and date {transaction.date} determined to be correct.")
        else:
            print(f"No splits found for transaction {transaction.id}. Exiting program.")
            quit()

# submit splits to ynab
def submit_splits_to_ynab(transactions):
    print("\nSubmitting splits to YNAB.")
    for transaction in transactions:
        if transaction.subtransactions:
            print(f"Submitting splits for transaction {transaction.id}. Amount: {transaction.amount}, Date: {transaction.date}.")
            
            # Prepare the data for the API request
            # reference: https://api.ynab.com/v1#/Transactions/updateTransaction
            data = {
                "transaction": {
                    "amount": int(transaction.amount * -1000),
                    "date": transaction.date.strftime('%Y-%m-%d'),
                    "memo": transaction.memo,
                    "cleared": transaction.cleared,
                    "approved": transaction.approved,
                    "flag_color": transaction.flag_color,
                    "account_id": transaction.account_id,
                    "payee_id": transaction.payee_id,
                    "payee_name": transaction.payee_name,
                    "category_id": transaction.category_id,
                    "subtransactions": transaction.subtransactions
                }
            }
            
            # Define the API endpoint and headers
            url = f"https://api.ynab.com/v1/budgets/{ynab_budget_id}/transactions/{transaction.id}"
            headers = {
                "Authorization": f"Bearer {ynab_api_token}",
                "Content-Type": "application/json"
            }

            # Make the API request
            response = requests.put(url, headers=headers, data=json.dumps(data))
            
            # Check if the request was successful
            if response.status_code == 200:
                print(f"Successfully submitted splits for transaction {transaction.id}.")
            else:
                print(f"Error submitting splits for transaction {transaction.id}: {response.status_code}")
                print(response.text)
        else:
            print(f"No splits found for transaction {transaction.id}. Exiting program.")
            quit()


# Display information about each transaction
def print_transactions(transactions):
    print("\nTransactions:")
    for transaction_instance in transactions:
        print(f"\nTransaction ID: {transaction_instance.id}")
        print(f"Payee Name: {transaction_instance.payee_name}")
        print(f"Category Name: {transaction_instance.category_name}")
        print(f"Date: {transaction_instance.date}")
        print(f"Amount: {transaction_instance.amount}")
        #print(f"Account Name: {transaction_instance.account_name}")
        #print(f"Memo: {transaction_instance.memo}")
        if transaction_instance.bidrl_invoice is None:
            print("BidRL Invoice: None")
        else:
            print(f"BidRL Invoice ID: {transaction_instance.bidrl_invoice.id}")

def print_invoices(invoices):
    print("\nInvoices:")
    for invoice in invoices:
        print(f"\nInvoice ID: {invoice.id}")
        print(f"Invoice Date: {invoice.date}")
        print(f"Invoice Total Cost: {invoice.total_cost}")
        print(f"Items: {len(invoice.items)}")


def ynab_invoice_transaction_split_main():
    # define number of days that the transaction date and invoice date can be different and still be considered a match
    # program will also look back this number of days past the oldest invoice date
    date_match_tolerance_def = 3

    # print out all Uncategorized transactions with the payee "BidRL SC"
    transactions = get_ynab_transactions('BidRL SC', 'uncategorized')

    # display the transactions
    print_transactions(transactions)

    # get the oldest transaction date
    oldest_transaction_date = get_oldest_transaction_date(transactions)
    print(f"\nOldest transaction date: {oldest_transaction_date}")
    oldest_transaction_date -= timedelta(days=date_match_tolerance_def)
    print(f"\nSubtracted date_match_tolerance from oldest_transaction_date. New oldest_transaction_date: {oldest_transaction_date}")

    # scrape invoices from bidrl
    invoices = get_processed_bidrl_invoices(oldest_transaction_date)

    # display the invoices
    print_invoices(invoices)

    # match transactions to invoices
    match_transactions_to_invoices(transactions
                                   , invoices
                                   , date_match_tolerance = date_match_tolerance_def
                                   , cost_match_tolerance = 0.02
                                   , verbose=True)

    # display the transactions
    print_transactions(transactions)

    # process transaction-invoice matches into splits
    split_transactions(transactions)

    # check the splits to ensure correctness before submitting to YNAB
    check_split_transactions(transactions)

    # after splits are processed, submit them to ynab
    submit_splits_to_ynab(transactions)

    # wait until user presses a key to exit
    input("Press any key to exit.")




if __name__ == "__main__":
    ynab_invoice_transaction_split_main()






'''
plan

- when bidrl transactions come in, ynab labels them "BidRL SC" and leaves them uncategorized
- the script will then
    - read the "BidRL SC" transactions that are uncategorized
    - note the oldest date of these transactions
    - scrape all invoices from bidrl starting from the oldest date noted
    - match each transaction in ynab with an invoice from the scrape
    - split each ynab transaction up with a line for each item in the invoice
    - fill in the total cost of each item based on the invoice
    - ensure that the sum of all items in the invoice add up to the total cost of the transaction
        - handle the case where it does not add up
            - print the transactions that are not being matched before exiting, making no changes to ynab
    - fill in the memo field with the url of the item
    - if everything is successful, submit the changes to our ynab transactions
- if the item is listed as 'b' or 'n', automatically categorize as '[b/n] Personal Money'
- if the item is listed as 't', then leave it as Uncategorized



'''