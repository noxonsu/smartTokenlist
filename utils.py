import json
import os
import requests
from time import sleep
def get_unique_domains():
    # Load bnb_erc20.json and find only domains
    with open("bnb_erc20.json", "r") as f:
        existing_data = json.load(f)

    # Extract all domains
    all_domains = [domain for entry in existing_data for domain in entry.get('web_domains', [])]

    # Convert to set to remove duplicates
    unique_domains = set(all_domains)

    #skip domains that are in ignoredomains.txt
    with open('ignoredomains.txt', 'r') as file:
        IGNORED_DOMAINS = set(file.read().split(','))
    unique_domains = [domain for domain in unique_domains if domain not in IGNORED_DOMAINS]

    return unique_domains


def get_holders_count(contract_address):
    url = f'https://api.chainbase.online/v1/token/holders?chain_id=56&contract_address={contract_address}&page=1&limit=20'
    headers = {
        'accept': 'application/json',
        'x-api-key': os.environ['CHAINBASE_API']
    }
    sleep(1)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # Assuming the count of holders is contained in a field named 'count' in the response data
        return data['count']
    else:
        raise Exception(f'Failed to retrieve holders count: {response.text}')
