import json
import os
import requests

from pyrogram import Client, errors, types
import json

from time import sleep
from pyrogram import errors

TELEGRAM_API_ID = int(os.environ.get('TELEGRAM_API_ID'))
TELEGRAM_API_HASH = os.environ.get('TELEGRAM_API_HASH')
TELEGRAM_SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
MAINFILE = os.environ.get("MAINFILE")

def catch_flood_wait(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except errors.FloodWait as e:
            wait_time = e.x + 10  # Note: It might be e.x depending on the Pyrogram version.
            print(f"Spam block, waiting for {wait_time} seconds before continuing")
            sleep(wait_time)
            return wrapper(*args, **kwargs)
    return wrapper


def load_and_filter_chats():
    with open(MAINFILE, 'r') as f:
        data = json.load(f)
        # Filtering based on given conditions
        filtered_data = [
            entry for entry in data
            if "tgGroupJoined" in entry
            and entry["tgGroupJoined"] == "success"  
            and "tgProposalSent" in entry
            and "error" in entry["tgProposalSent"]
        ]
        
        return data, filtered_data


def main():
    app = Client('TgSession', session_string=TELEGRAM_SESSION_STRING, api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH)
    print('Bot starting...')
    app.start()
    me = app.get_me()
    print(f'Bot started as {me.username}')
    print('Bot successfully started!')
    all_data, filtered_chats = load_and_filter_chats()
    
    # Initialize left_chat_ids before using it
    left_chat_ids = []
    
    for entry in filtered_chats:
        chat_id = entry.get('tgGroupJoined')
        myuser_id = entry.get('myuser')
        
        if myuser_id and myuser_id != me.id:
            print("You joined from another account!")
            continue
        
        if chat_id:
            @catch_flood_wait
            def leave_and_log(chat_id):
                print(f"Leaving chat with ID: {chat_id}")
                app.leave_chat(chat_id, delete=True)  # Leaving and deleting the dialog
                print(f"Successfully left chat with ID: {chat_id}")

            try:
                leave_and_log(chat_id)
                left_chat_ids.append(chat_id)  # Adding chat_id to the list
                
                for data_entry in all_data:
                    if data_entry.get('tgGroupJoined') == chat_id:
                        data_entry['tgGroupJoined'] = "leaved"
                        break
            except Exception as e:
                print(f"Error while leaving chat with ID: {chat_id}. Error: {e}")

    # Save chat IDs to a .txt file
    with open('left_chats.txt', 'w') as txt_file:
        for chat_id in left_chat_ids:
            txt_file.write(f"{chat_id}\n")

    # Save the updated data back to bnb_erc20.json
    with open(MAINFILE, 'w') as file:
        json.dump(all_data, file, indent=2)

if __name__ == '__main__':
    main()