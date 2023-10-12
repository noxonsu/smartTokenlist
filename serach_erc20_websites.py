"""
Script to update the 'eth_uniswap_weekly_top.json' file by fetching missing ERC20 token names
using an Infura Ethereum node.
"""

import json
from web3 import Web3

# Connect to Infura Ethereum mainnet
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/950fd8f28b864725867d440676e7bd60'))

# Ensure you are connected
if not w3.is_connected():
    print("Not connected to Ethereum node!")
    exit()

# ERC20 ABI
erc20_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

def get_token_name(contract_address):
    contract = w3.eth.contract(address=contract_address, abi=erc20_abi)
    return contract.functions.name().call()

with open('eth_uniswap_weekly_top.json', 'r') as file:
    data = json.load(file)

# Counter for items without erc20name
count = 0

for item in data:
    # Check if erc20name is missing and counter is less than 10
    if 'erc20name' not in item and count < 10:
        contract_address = item['targetToken']
        try:
            erc20_name = get_token_name(contract_address)
        except Exception:
            erc20_name = "not found"
        item['erc20name'] = erc20_name
        count += 1


with open('eth_uniswap_weekly_top_updated.json', 'w') as file:
    json.dump(data, file, indent=4)
