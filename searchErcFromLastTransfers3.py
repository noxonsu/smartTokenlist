import os
import json
import datetime
import time
from requests import get, post

# API Key from Environment Variable
API_KEY = os.environ.get("DUNE_API_KEY")

# Base URL
BASE_URL = "https://api.dune.com/api/v1/"

def execute_query(query_id):
    url = f"{BASE_URL}query/{query_id}/execute"
    params = {"api_key": API_KEY}
    response = post(url, params=params)
    if response.status_code == 200:
        print("Query execution triggered.")
    else:
        print(f"Error in query execution: {response.json().get('error')}")

def get_query_results(query_id):
    url = f"{BASE_URL}query/{query_id}/results"
    params = {"api_key": API_KEY}
    response = get(url, params=params)
    if response.status_code == 200:
        return response.json().get('result', {}).get('rows', [])
    else:
        print(f"Error: {response.json().get('error')}")
        return None

def main():
    query_id = "3099609"
    execute_query(query_id)  # Trigger the query execution
    time.sleep(5)  # Wait for 5 seconds (note: you mentioned 15 seconds in the comment, but the sleep time is set to 5)

    query_results = get_query_results(query_id)
    if not query_results:
        return

    date_add = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Load existing data
    try:
        with open("bnb_erc20.json", "r") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = []

    existing_tokens = {entry['contract_address'] for entry in existing_data}

    new_contracts_count = 0  # Counter for new contracts

    for row in query_results:
        contract_address = row.get('contract_address', '')

        # If the contract_address exists and is NOT in the existing tokens set, then append to the list
        if contract_address and contract_address not in existing_tokens:
            existing_data.append({
                "contract_address": contract_address
            })
            existing_tokens.add(contract_address)  # Update the set with the new address
            new_contracts_count += 1  # Increment the counter

    # Save to JSON file
    with open("bnb_erc20.json", "w") as f:
        json.dump(existing_data, f, indent=4)

    # Print the total number of new contracts added
    print(f"Total number of new contracts added: {new_contracts_count}")

if __name__ == "__main__":
    main()

