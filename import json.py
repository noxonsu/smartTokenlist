import json

def reset_sites_for_reprocessing(filepath, holder_threshold=500, num_to_reset=50):
    """
    Resets specific fields in entries of a JSON file to trigger reprocessing.

    Criteria for selecting entries:
    - Have a 'holders' count in the 'ETH' network (or other specified network) less than the threshold.
    - Have 'web_domains' key
    - Have 'contract_address' key

    Fields to reset:
    - 'processedGpt' (set to False)
    - 'p6' (remove if exists)
    - 'telegram_groups' (set to empty list)
    - 'emails' (set to empty list)

    Args:
        filepath: The path to the JSON file.
        holder_threshold: The maximum number of holders for a site to be considered for reprocessing.
        num_to_reset: The number of sites to reset, starting from the end of the list.
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

    # Filter entries that meet the criteria
    eligible_entries = [
        entry for entry in data
        if 'holders' in entry
        and 'ETH' in entry['holders']
        and entry['holders']['ETH'] < holder_threshold
        and 'web_domains' in entry
        and 'contract_address' in entry
    ]

    # Select the last 'num_to_reset' entries
    entries_to_reset = eligible_entries[-num_to_reset:]

    reprocessed_count = len(entries_to_reset)
    for entry in entries_to_reset:
        # Reset the fields
        entry['processedGpt'] = False
        entry.pop('p6', None)  # Remove 'p6' if it exists
        entry['telegram_groups'] = []  # Set to empty list
        entry['emails'] = []  # Set to empty list
        print(f"Reset entry: contract_address={entry['contract_address']}, holders={entry['holders']['ETH']}")



    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully modified {filepath}. Reprocessed {reprocessed_count} entries.")
    except Exception as e:
        print(f"Error writing to file: {e}")


# Example usage:
filepath = "/workspaces/smartTokenlist/eth_erc20.json"  # Replace with your file path
reset_sites_for_reprocessing(filepath, num_to_reset=50)