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
        'tgProposalSent' not in data and # "tgProposalSent" is not set
        'holders' not in data
    )

def main():
    # Load the JSON file
    with open('bnb_erc20.json', 'r') as f:
        content = json.load(f)

    # Track the indices of items that pass the filter
    filtered_indices = [i for i, item in enumerate(content) if filter_data(item)]
    
    # Iterate over filtered indices to update corresponding items in content
    for index in filtered_indices:
        item = content[index]
        contract_address = item.get('contract_address')
        if contract_address:
            holders_count = get_holders_count(contract_address)
            print ("\n"+contract_address)
            print (holders_count)
            item['holders'] = {"bsc": holders_count}

        # Remove 'tgGroupJoined' and 'myuser' fields
        item.pop('tgGroupJoined', None)
        item.pop('myuser', None)

    # Save the entire updated content list back to the JSON file
    with open('bnb_erc20.json', 'w') as f:
        json.dump(content, f, indent=4)


if __name__ == "__main__":
    main()

