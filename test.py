import os
import re
import json
from time import sleep

from pyrogram import Client, errors, types
TELEGRAM_API_ID = int(os.environ.get('TELEGRAM_API_ID'))
TELEGRAM_API_HASH = os.environ.get('TELEGRAM_API_HASH')

with open('bnb_erc20.json', 'r') as f:
    data = json.load(f)

def is_numeric_and_positive(value):
    try:
        numeric_value = float(value)
        return numeric_value > 0
    except (ValueError, TypeError):
        return False



groups_with_sent_proposal = [entry for entry in data 
                             if "tgProposalSent" in entry 
                             and is_numeric_and_positive(entry["tgProposalSent"]) 
                             ]

print(f"Found {len(groups_with_sent_proposal)} groups with sent proposal")

TELEGRAM_SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
app = Client('TgSession', session_string=TELEGRAM_SESSION_STRING, api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH)
print('Bot starting...')
app.start()

all = ""
for entry in groups_with_sent_proposal:
    all = all + "https://t.me/" + str(entry["telegram_groups"][0]) + "/" + str(entry["tgProposalSent"]) + " sent " + str(entry["contract_address"]) + "\n" + str(entry['web_domains'][0]) + "\n\n"
app.send_message(-1001904539844, text=all) # logs
print('All done!')