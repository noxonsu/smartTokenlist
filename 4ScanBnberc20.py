import os
import json
import re
import time
from requests import get
from utils import *
BNBSCAN_API_KEY = os.environ.get("BNBSCAN_API_KEY")
ETHSCAN_BASE_URL = os.environ.get("ETHSCAN_BASE_URL")
MAINFILE = os.environ.get("MAINFILE")
CHAINBASE_API_URL= os.environ.get("CHAINBASE_API_URL")
DUNE_QUERY= os.environ.get("DUNE_QUERY")
NETWORK= os.environ.get("NETWORK")
def get_contract_source(address):
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": BNBSCAN_API_KEY
    }
    response = get(ETHSCAN_BASE_URL, params=params)
    if response.status_code == 200:
        # Parse rate limit headers
        rate_limit = response.headers.get('X-RateLimit-Limit')
        rate_remaining = response.headers.get('X-RateLimit-Remaining')
        rate_reset = response.headers.get('X-RateLimit-Reset')
        
        return response.json()
    return None

def extract_data_from_source(source_code):
    # Load ignored domains from file
    with open('ignoredomains.txt', 'r') as file:
        IGNORED_DOMAINS = set(file.read().split(','))

    # Extract data from the source code
    web_domains = re.findall(r'https?://([\w\-\.]+)', source_code)
    telegram_groups = re.findall(r'https://t\.me/(\w+)', source_code)
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', source_code)

    # Filter out ignored domains
    web_domains = [domain for domain in web_domains if domain not in IGNORED_DOMAINS]

    extracted_data = {}
    if web_domains:
        extracted_data["web_domains"] = web_domains
    if telegram_groups:
        extracted_data["telegram_groups"] = telegram_groups
    if emails:
        extracted_data["emails"] = emails

    return extracted_data


def main():
    # Load existing data
    try:
        with open(MAINFILE, "r") as f:
            contracts = json.load(f)
    except FileNotFoundError:
        contracts = []

    new_contracts_scanned = 0
    total_domains_found = 0

    # For each contract, check if scanned, if not get source and scan it
    for contract in contracts:
        if "sourceScanned" not in contract:
            new_contracts_scanned += 1
            print(f"Fetching source code for {contract['contract_address']}...")
            response = get_contract_source(contract['contract_address'])
            
            # If the source code retrieval was successful
            if response and response.get('status') == "1":
                source_code = response['result'][0].get('SourceCode', '')
                
                # Extract the desired data from the source code
                extracted_data = extract_data_from_source(source_code)
                
                # Update the contract data
                contract["sourceScanned"] = "processed"

                

                contract.update(extracted_data)

                if "web_domains" in extracted_data:
                    total_domains_found += 1

            # If there was an error or no source code
            else:
                contract["sourceScanned"] = "failed"

            holders_count = get_holders_count(contract['contract_address'])

            contract['holders'] = {f"{NETWORK}": holders_count}

            # Save the updated data in each iteration
            with open(MAINFILE, "w") as f:
                json.dump(contracts, f, indent=4)

            #time.sleep(1)  # Avoid hitting the API rate limit

    print(f"Total new contracts scanned: {new_contracts_scanned}")
    print(f"Total new domains found: {total_domains_found}")

if __name__ == "__main__":
    main()

