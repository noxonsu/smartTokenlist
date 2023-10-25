import json
import os

from utils import get_holders_count  # Assuming get_holders_count is defined in utils.py

def filter_data(data):
    # Filtering conditions
    return (
        data.get('web_domains') and  # "web_domains" is not empty
        data.get('p6', False) and  # "p6" is True
        data.get('myuser') == 6003957640 and  # "myuser" is 6003957640
        data.get('tgGroupJoined') == 'success' and  # "tgGroupJoined" is 'success'
        'tgProposalSent' not in data  # "tgProposalSent" is not set
    )

def main():
    # Load the JSON file
    with open('bnb_erc20.json', 'r') as f:
        content = json.load(f)
    
    # Filter the data
    filtered_data = list(filter(filter_data, content))
    filtered_data = filtered_data[:1]
    # Iterate over filtered data to call get_holders_count and update the data
    for item in filtered_data:
        contract_address = item.get('contract_address')
        if contract_address:
            holders_count = get_holders_count(contract_address)
            item['holders'] = {"bsc": holders_count}

    # Print the updated filtered data
    print(json.dumps(filtered_data, indent=4))

if __name__ == "__main__":
    main()
