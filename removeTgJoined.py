import json

def filter_domains_from_json():
    # Load bnb_erc20.json
    with open(MAINFILE, "r", encoding='utf-8') as f:
        existing_data = json.load(f)

    # Load ignored domains from ignoredomains.txt
    with open('ignoredomains.txt', 'r', encoding='utf-8') as file:
        IGNORED_DOMAINS = set(file.read().split(','))

    # Remove the tgGroupJoined field from each item in the existing data
    if isinstance(existing_data, list):
        for item in existing_data:
            if "tgGroupJoined" in item:
                del item["tgGroupJoined"]
    elif isinstance(existing_data, dict):  # If data is a dictionary
        if "tgGroupJoined" in existing_data:
            del existing_data["tgGroupJoined"]

    # Save the modified data back to bnb_erc20.json
    with open(MAINFILE, "w", encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)

filter_domains_from_json()
