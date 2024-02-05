import json
import os
import requests
import sys
from datetime import datetime, timedelta

def load_existing_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def create_github_issue(token, title, body):
    url = "https://api.github.com/repos/noxonsu/chains/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "title": title,
        "body": body
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"Successfully created Issue {title}")
    else:
        print(f"Failed to create issue {title}")
        print(response.json())

def check_existing_issue(token, title, existing_issues_cache):
    page = 1
    while True:
        url = f"https://api.github.com/repos/noxonsu/smartTokenlist/issues?state=all&page={page}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            issues = response.json()
            if not issues:
                break
            for issue in issues:
                existing_issues_cache.add(issue["title"])
                if issue["title"] == title:
                    return True
            page += 1
        else:
            break
    return False

if __name__ == "__main__":
    

    #github_token = sys.argv[1]
    existing_data = load_existing_data("eth_erc20.json")
    
    # Example of data structure
    """
        {
            "contract_address": "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce",
            "sourceScanned": "processed",
            "web_domains": [
                "tokenmint.io"
            ],
            "holders": {
                "ETH": 1354770
            },
            "telegram_groups": [],
            "p6": true
        },
    """
    
    #select only elements with p8 = true and save to eth_erc20_p8.json file
    total_items_scanned = 0 
    filtered_data = []
    for item in existing_data:
        total_items_scanned += 1
        if "p8" in item and item["p8"] == True:
            filtered_data.append(item)
            
    
    with open("eth_erc20_p8.json", "w") as f:
        json.dump(filtered_data, f, indent=4)
        
    

    print(f"Total items scanned: {total_items_scanned}")
