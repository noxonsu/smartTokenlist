import json

def main():
    # Load bnb_erc20.json and find only domains
    with open("bnb_erc20.json", "r") as f:
        existing_data = json.load(f)

    # Extract all domains
    all_domains = [domain for entry in existing_data for domain in entry.get('web_domains', [])]

    # Convert to set to remove duplicates
    unique_domains = set(all_domains)

    # Print the unique domains
    for domain in unique_domains:
        print(domain)

if __name__ == "__main__":
    main()
