def get_unique_domains():
    # Load bnb_erc20.json and find only domains
    with open("bnb_erc20.json", "r") as f:
        existing_data = json.load(f)

    # Extract all domains
    all_domains = [domain for entry in existing_data for domain in entry.get('web_domains', [])]

    # Convert to set to remove duplicates
    unique_domains = set(all_domains)

    #skip domains that are in ignoredomains.txt
    with open('ignoredomains.txt', 'r') as file:
        IGNORED_DOMAINS = set(file.read().split(','))
    unique_domains = [domain for domain in unique_domains if domain not in IGNORED_DOMAINS]

    return unique_domains