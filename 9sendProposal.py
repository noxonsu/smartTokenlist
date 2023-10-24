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
    file_path = f"proposals/{contract_address}.json"
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data["proposal"]
    except Exception as e:
        print(f"Error loading proposal text for {contract_address}: {e}")
        return None

def load_sent_chats():
    try:
        with open('proposalSent.txt', 'r') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []
    
def save_sent_chat(chat_link):
    with open('proposalSent.txt', 'a') as f:
        f.write(f"{chat_link}\n")

@catch_flood_wait
@catch_flood_wait
def send_proposal(app, chat_id, contract_address):
    sent_chats = load_sent_chats()
    if chat_id in sent_chats:
        raise Exception(f"Proposal already sent to {chat_id}, skipping...")

    proposal_text = load_proposal_text(contract_address)
    if proposal_text:
        # Send to debug chat if DEBUG_MODE is True
        target_chat_id = DEBUG_CHAT_ID if DEBUG_MODE else chat_id
        try:
            message = app.send_message(chat_id=target_chat_id, text=proposal_text)  # Capture the result
            message_link = f"{message.id}"  # Construct the message link
            # Save chat_id if debug mode = false
            if not DEBUG_MODE:
                save_sent_chat(target_chat_id)  
            return message_link
        except errors.RPCError as e:
            # Check for the specific error and handle it
            if "@SpamBot" in str(e):
                print(app.send_message("SpamBot", text="/start"))
                sleep(3)
                print (app.send_message("SpamBot", text="/start"))
                print(f"Sent a message to @SpamBot due to restriction for chat {chat_id}")
            raise Exception(f"Telegram says: {e}") 
    else:
        raise Exception(f"No proposal text found for contract address: {contract_address}")




def main():
    with open('bnb_erc20.json', 'r') as f:
        data = json.load(f)
    
    groups_to_send_proposal = [entry for entry in data if entry.get("tgGroupJoined") == "success"and entry.get("p8") == True and "tgProposalSent" not in entry]
    
    print(f"Found {len(groups_to_send_proposal)} groups to send proposal to")
    
    groups_to_send_proposal = groups_to_send_proposal[:10]

    TELEGRAM_SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
    
    if TELEGRAM_SESSION_STRING is None:
        print("save TELEGRAM_SESSION_STRING session string to env: ")
        return False

    with Client('TgSession', session_string=TELEGRAM_SESSION_STRING, api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH) as app:
        print('Bot starting...')
        
        for entry in groups_to_send_proposal:
            chat_link = entry["telegram_groups"][0]  # Picking the first group to send the proposal
            ok=False
            try:
                message_link = send_proposal(app, chat_link, entry["contract_address"])
                # Update status after sending proposal
                entry["tgProposalSent"] = message_link
                ok = True
            except Exception as e:
                print(f"Error processing {chat_link}: {e}")
                entry["tgProposalSent"] = f"error: {e}"

            if ok:
                print(f"Sent proposal to {chat_link}. Waiting and send responses to debug group")
                sleep(30)
                lastm = "https://t.me/"+chat_link+"/"+message_link
                for message in app.get_chat_history(entry["telegram_groups"][0], limit=5):
                    if message.text and len(message.text) <= 120:
                        lastm += message.text + "\n"
                app.send_message(-1001904539844, text=lastm)

        
        with open('bnb_erc20.json', 'w') as f:
            json.dump(data, f, indent=4)

    print('All done!')


if __name__ == '__main__':
    main()
