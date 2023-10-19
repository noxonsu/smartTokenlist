import json

# Load the data
with open('bnb_erc20.json', 'r') as file:
    data = json.load(file)

# Filter the entries and remove specified fields
for entry in data:
    if 'tgProposalSent' in entry and 'USER_BANNED_IN_CHANNEL' in entry['tgProposalSent']:
        entry.pop('processedGpt', None)
        entry.pop('tgGroupJoined', None)
        entry.pop('tgProposalSent', None)

# Save the modified data back to the file
with open('bnb_erc20.json', 'w') as file:
    json.dump(data, file, indent=2)
