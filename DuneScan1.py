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
    query_id = "3009199"
    execute_query(query_id)  # Trigger the query execution
    time.sleep(15)  # Wait for 15 seconds

    query_results = get_query_results(query_id)
    if not query_results:
        return

    date_add = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Load existing data
    try:
        with open("eth_uniswap_weekly_top.json", "r") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = []

    existing_tokens = {entry['targetToken'] for entry in existing_data}

    # Add new data
    for row in query_results:
        token_pair = row.get('token_pair', '')
        target_token = token_pair.split('-')[0]

        if target_token not in existing_tokens:
            existing_data.append({
                "token_pair": token_pair,
                "targetToken": target_token,
                "dateAdd": date_add
            })
            existing_tokens.add(target_token)

    # Save to JSON file
    with open("eth_uniswap_weekly_top.json", "w") as f:
        json.dump(existing_data, f, indent=4)

if __name__ == "__main__":
    main()
