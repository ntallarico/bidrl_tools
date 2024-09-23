import requests
import json
from config import ynab_api_token, ynab_budget_id, ynab_category_dict


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


def get_ynab_transactions():
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
        
        # Print each transaction
        for transaction in transactions:
            print(f"Date: {transaction['date']}")
            print(f"Payee: {transaction['payee_name']}")
            print(f"Category: {transaction['category_name']}")
            print(f"Amount: ${transaction['amount']/1000:.2f}")  # Amount is in milliunits
            print(f"Memo: {transaction['memo']}")
            print("---")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

#get_ynab_transactions()


def get_ynab_transactions(payee=None):
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
        
        # Print transactions for the specified payee
        for transaction in transactions:
            if payee is None or transaction['payee_name'] == payee:
                print(f"Date: {transaction['date']}")
                print(f"Payee: {transaction['payee_name']}")
                print(f"Category: {transaction['category_name']}")
                print(f"Amount: ${transaction['amount']/1000:.2f}")  # Amount is in milliunits
                print(f"Memo: {transaction['memo']}")
                print("---")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

#get_ynab_transactions('Walmart')  # Get transactions for Walmart
# get_ynab_transactions()  # Get all transactions


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
        # Print transactions for the specified payee and categorized status
        for transaction in transactions:
            if (payee is None or transaction['payee_name'] == payee) and \
               (categorized == 'all' or 
                (categorized == 'categorized' and transaction['category_name'] != 'Uncategorized') or 
                (categorized == 'uncategorized' and transaction['category_name'] == 'Uncategorized')):
                print(transaction)
                print(f"Date: {transaction['date']}")
                print(f"Payee: {transaction['payee_name']}")
                print(f"Category: {transaction['category_name']}")
                print(f"Amount: ${transaction['amount']/1000:.2f}")  # Amount is in milliunits
                print(f"Memo: {transaction['memo']}")
                print("---")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

#get_ynab_transactions('Walmart', 'categorized')  # Get categorized transactions for Walmart
# get_ynab_transactions()  # Get all transactions

#get_ynab_transactions('BidRL SC', 'uncategorized')


def get_category_ids(ynab_category_dict):
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
            if value in category_name_to_id:
                updated_dict[key] = category_name_to_id[value]
            else:
                updated_dict[key] = None  # or handle the case where the category name is not found
        
        return updated_dict
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

print(get_category_ids(ynab_category_dict))