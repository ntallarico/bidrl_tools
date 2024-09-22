import requests
import json
from config import ynab_api_token, ynab_budget_id


class Transaction:
    def __init__(self
                 , id: str = None
                 , date: str = None
                 , amount: int = None
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
                 , subtransactions: list = None):
        
        self._check_type('id', id, str)
        self._check_type('date', date, str)
        self._check_type('amount', amount, int)
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

        self.id = id
        self.date = date
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

    def _check_type(self, name, value, expected_type):
        if value is not None and not isinstance(value, expected_type):
            raise TypeError(f"Expected {name} to be {expected_type.__name__}, got {type(value).__name__}")

    def display(self):
        print(f"Transaction ID: {self.id}")
        print(f"Date: {self.date}")
        print(f"Amount: {self.amount}")
        print(f"Memo: {self.memo}")
        print(f"Cleared: {self.cleared}")
        print(f"Approved: {self.approved}")
        print(f"Flag Color: {self.flag_color}")
        print(f"Account ID: {self.account_id}")
        print(f"Payee ID: {self.payee_id}")
        print(f"Category ID: {self.category_id}")
        print(f"Transfer Account ID: {self.transfer_account_id}")
        print(f"Transfer Transaction ID: {self.transfer_transaction_id}")
        print(f"Matched Transaction ID: {self.matched_transaction_id}")
        print(f"Import ID: {self.import_id}")
        print(f"Deleted: {self.deleted}")
        print(f"Account Name: {self.account_name}")
        print(f"Payee Name: {self.payee_name}")
        print(f"Category Name: {self.category_name}")
        print(f"Subtransactions: {self.subtransactions}")
    




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
        transaction_list = []

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
                    amount=transaction['amount'],
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
                transaction_list.append(transaction_instance)
        
        # Display information about each transaction
        for transaction_instance in transaction_list:
            transaction_instance.display()
            print("\n")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)




def ynab_invoice_transaction_split_main():
    # print out all Uncategorized transactions with the payee "BidRL SC"
    get_ynab_transactions('BidRL SC', 'uncategorized')

    #

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