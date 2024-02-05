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
        url = f"https://api.github.com/repos/noxonsu/chains/issues?state=all&page={page}"
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
    if len(sys.argv) < 2:
        print("Usage: python script.py <GitHub_Token>")
        sys.exit(1)

    github_token = sys.argv[1]
    existing_data = load_existing_data("eth_erc20.json")

    # Get the current date and time
    now = datetime.now()

    # Initialize cache for existing issues
    existing_issues_cache = set()

    # Initialize counter for total items scanned
    total_items_scanned = 0

    for item in existing_data:
        date_add_str = item.get("dateAdd", None)
        
        if date_add_str:
            try:
                date_add = datetime.strptime(date_add_str, '%Y-%m-%dT%H:%M:%S.%f')
                days_diff = (now - date_add).days
            except ValueError:
                print(f"Invalid date format for item with chainId {item.get('chainId', 'Unknown')}")
                days_diff = None
        else:
            days_diff = None

        if days_diff is not None and days_diff <= 2:
            total_items_scanned += 1  # Increment the counter
            chain_id = item.get("chainId", "Unknown")
            ticker = item.get("ticker", "Unknown")
            title = f"ADD {chain_id} {ticker}"

            if title not in existing_issues_cache and not check_existing_issue(github_token, title, existing_issues_cache):
                body = json.dumps(item, indent=4)
                create_github_issue(github_token, title, body)

    print(f"Total items scanned: {total_items_scanned}")
