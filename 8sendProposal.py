import os
import json
from time import sleep
from pyrogram import Client, errors

TELEGRAM_API_ID = int(os.environ.get('TELEGRAM_API_ID'))
TELEGRAM_API_HASH = os.environ.get('TELEGRAM_API_HASH')
DEBUG_CHAT_ID = 'testonoutgroup'  # replace with your test chat username or ID
DEBUG_MODE = False  # Set to False for live mode


def catch_flood_wait(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except errors.FloodWait as e:
            wait_time = e.value + 20
            print(f"Spam block, waiting for {wait_time} seconds before continuing")
            sleep(wait_time)
            return wrapper(*args, **kwargs)
    return wrapper

def load_proposal_text(contract_address):
    file_path = f"texts/{contract_address}.json"
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data["proposal"]
    except Exception as e:
        print(f"Error loading proposal text for {contract_address}: {e}")
        return None

@catch_flood_wait
def send_proposal(app, chat_id, contract_address):
    proposal_text = load_proposal_text(contract_address)
    if proposal_text:
        # Send to debug chat if DEBUG_MODE is True
        target_chat_id = DEBUG_CHAT_ID if DEBUG_MODE else chat_id
        app.send_message(chat_id=target_chat_id, text=proposal_text)
    else:
        raise Exception(f"No proposal text found for contract address: {contract_address}")


def load_groups_to_send_proposal():
    with open('bnb_erc20.json', 'r') as f:
        data = json.load(f)
        return [entry for entry in data if entry.get("tgGroupJoined") == "success" and "tgProposalSent" not in entry]

def main():
    with open('bnb_erc20.json', 'r') as f:
        data = json.load(f)
    groups_to_send_proposal = [entry for entry in data if entry.get("tgGroupJoined") == "success" and "tgProposalSent" not in entry]
    groups_to_send_proposal = groups_to_send_proposal[:5]

    with Client('TgSession', api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH) as app:
        print('Bot starting...')
        for entry in groups_to_send_proposal:
            chat_link = entry["telegram_groups"][0]  # Picking the first group to send the proposal
            try:
                send_proposal(app, chat_link, entry["contract_address"])
                # Update status after sending proposal
                entry["tgProposalSent"] = "success"
            except Exception as e:
                print(f"Error processing {chat_link}: {e}")
                entry["tgProposalSent"] = f"error: {e}"

        # Save updated status to the JSON file
        with open('bnb_erc20.json', 'w') as f:
            json.dump(data, f, indent=4)

    print('All done!')


if __name__ == '__main__':
    main()
