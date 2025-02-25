import json

def remove_last_50_sites_with_low_holders(filepath, holder_threshold=500):
    """
    Removes the last 50 entries from a JSON array that meet the criteria:
    - Have a 'holders' count in the 'ETH' network (or other specified network) less than the threshold.
    - Have 'web_domains' key

    Args:
        filepath: The path to the JSON file.
        holder_threshold: The maximum number of holders for a site to be considered for removal.
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

    # Filter and sort entries based on holders count and web_domains presence
    eligible_entries = []
    for i, entry in enumerate(data):
        if 'holders' in entry and 'ETH' in entry['holders'] and entry['holders']['ETH'] < holder_threshold and 'web_domains' in entry:
            eligible_entries.append((i, entry))

    eligible_entries.sort(key=lambda x: x[0], reverse=True)  # Sort by index in descending order

    # Remove up to 50 eligible entries
    removed_count = 0
    indices_to_remove = []
    for i, (index, _) in enumerate(eligible_entries):
        if removed_count < 50:
            indices_to_remove.append(index)
            removed_count += 1
        else:
          break

    indices_to_remove.sort(reverse=True)  # Sort in descending order to avoid index issues when removing

    for index in indices_to_remove:
        removed_item = data.pop(index)
        print(f"Removed entry at index {index}, contract_address: {removed_item.get('contract_address')}, holders: {removed_item.get('holders', {}).get('ETH', 'N/A')}")


    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully modified {filepath}")
    except Exception as e:
        print(f"Error writing to file: {e}")


# Example usage (assuming the file is named eth_erc20.json in the current directory):
filepath = "/workspaces/smartTokenlist/eth_erc20.json"
remove_last_50_sites_with_low_holders(filepath)
