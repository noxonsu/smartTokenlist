import os
import json
import re
import time
from requests import get

BNBSCAN_API_KEY = os.environ.get("BNBSCAN_API_KEY")
BNBSCAN_BASE_URL = "https://api.bscscan.com/api"

def get_contract_source(address):
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": BNBSCAN_API_KEY
    }
    response = get(BNBSCAN_BASE_URL, params=params)
    if response.status_code == 200:
        # Parse rate limit headers
        rate_limit = response.headers.get('X-RateLimit-Limit')
        rate_remaining = response.headers.get('X-RateLimit-Remaining')
        rate_reset = response.headers.get('X-RateLimit-Reset')
        
        return response.json()
    return None


def extract_data_from_source(source_code):
    # List of domains to ignore
    IGNORED_DOMAINS = {
        "docs.openzeppelin.com","consensys.github.io","ethereum.stackexchange.com","raw.githubusercontent.com","etherscan.io","x.com","github.com", "www.gnu.org", "fsf.org", "forum.openzeppelin.com",
        "en.wikipedia.org", "wizard.openzeppelin.com", "eips.ethereum.org",
        "medium.com", "blog.openzeppelin.com", "eth.wiki", "diligence.consensys.net",
        "solidity.readthedocs.io", "t.me", "forum.zeppelin.solutions",
        "web3js.readthedocs.io", "docs.ethers.io", "ethereum.github.io",
        "docs.metamask.io", "xn--2-umb.com", "cs.stackexchange.com",
        "docs.soliditylang.org", "hardhat.org", "twitter.com",
        "www.facebook.com", "www.instagram.com", "consensys.net"
    }

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
        with open("bnb_erc20.json", "r") as f:
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

            # Save the updated data in each iteration
            with open("bnb_erc20.json", "w") as f:
                json.dump(contracts, f, indent=4)

            #time.sleep(1)  # Avoid hitting the API rate limit

    print(f"Total new contracts scanned: {new_contracts_scanned}")
    print(f"Total new domains found: {total_domains_found}")

if __name__ == "__main__":
    main()

