import requests
import json
from config import ynab_api_token, ynab_budget_id


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
        
        # Print transactions from Walmart
        for transaction in transactions:
            if transaction['payee_name'] == 'Walmart':
                print(f"Date: {transaction['date']}")
                print(f"Payee: {transaction['payee_name']}")
                print(f"Category: {transaction['category_name']}")
                print(f"Amount: ${transaction['amount']/1000:.2f}")  # Amount is in milliunits
                print(f"Memo: {transaction['memo']}")
                print("---")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

get_ynab_transactions()