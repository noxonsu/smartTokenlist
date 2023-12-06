import json
import os

#load json file
with open('eth_erc20.json') as f:
    data = json.load(f)


# Sort the data by holders in descending order
sorted_data = sorted(data, key=lambda x: x["holders"]["ETH"], reverse=True)


# Extracting just the addresses
addresses = [item["contract_address"] for item in sorted_data]

# Comma separated addresses
comma_separated_addresses = ',\n '.join(addresses)
print(comma_separated_addresses)