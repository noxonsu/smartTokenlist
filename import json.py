import json

def remove_p6_from_last_30(filepath):
    """
    Removes the "p6": true field from the last 30 entries in a JSON array.

    Args:
        filepath: The path to the JSON file.
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filepath}")
        return

    num_entries = len(data)
    if num_entries < 30:
        print(f"Warning: The file has less than 30 entries ({num_entries}). Removing 'p6' from all entries.")
        start_index = 0
    else:
        start_index = num_entries - 30

    for i in range(start_index, num_entries):
        if "p6" in data[i] and data[i]["p6"] == True:
          del data[i]["p6"]
          print(f"Removed 'p6': true from entry at index {i}, contract_address: {data[i].get('contract_address')}")
    
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully modified {filepath}")
    except Exception as e:
        print(f"Error writing to file: {e}")


# Example usage (assuming the file is named eth_erc20.json in the current directory):
filepath = "/workspaces/smartTokenlist/eth_erc20.json" 
remove_p6_from_last_30(filepath)
