import os
import re
import json
from time import sleep

from pyrogram import Client, errors, types
TELEGRAM_API_ID = int(os.environ.get('TELEGRAM_API_ID'))
TELEGRAM_API_HASH = os.environ.get('TELEGRAM_API_HASH')

print(TELEGRAM_API_ID)

SUBSCRIBE_TO_LINKED_CHAT = 'true'

def catch_flood_wait(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except errors.FloodWait as e:
            wait_time = e.value + 10
            print(f"Spam block, waiting for {wait_time} seconds before continuing")
            sleep(wait_time)
            return wrapper(*args, **kwargs)
    return wrapper

@catch_flood_wait
def get_chat_with_retries(app, chat_link) -> types.Chat:
    return app.get_chat(chat_link)

@catch_flood_wait
def subscribe_to_chat_with_retries(app, chat_link, linked=False) -> types.Chat | None:
    linked_str = "linked chat " if linked else ""
    try:
        print(f'Subscribing to {linked_str}{chat_link}')
        chat = app.join_chat(chat_link)
        print(f'Successfully subscribed to {linked_str}{chat.title}')
        
        # Write to chats_success.txt
        with open('chats_success.txt', 'a') as f:
            f.write(f"{chat_link}\n")
        
    except errors.UserAlreadyParticipant:
        print(f'Already subscribed to {linked_str}{chat_link}')
    except errors.InviteRequestSent:
        print('The request to join this chat or channel has been successfully sent')

    if not linked:
        return get_chat_with_retries(app, chat_link)

def load_and_filter_chats():
    with open('bnb_erc20.json', 'r') as f:
        data = json.load(f)
        # Filtering based on given conditions
        return data, [
            entry for entry in data
            if "web_domains" in entry and entry["web_domains"] 
            and "telegram_groups" in entry and entry["telegram_groups"]
            and "processedGpt" in entry and entry["processedGpt"]
            and "tgGroupJoined" not in entry
        ]


def main():
    data, chats_to_subscribe = load_and_filter_chats()

    # Limit to processing only 6 groups
    chats_to_subscribe = chats_to_subscribe[:6]

    app = Client('Autosubscribe', api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH)
    print('Bot starting...')
    app.start()
    print('Bot successfully started!')

    for entry in chats_to_subscribe:
        chat_link = entry["telegram_groups"][0]
        try:
            chat = subscribe_to_chat_with_retries(app, chat_link)
            if SUBSCRIBE_TO_LINKED_CHAT:
                linked_chat = chat.linked_chat
                if linked_chat:
                    subscribe_to_chat_with_retries(app, linked_chat.id, linked=True)
                else:
                    print('No linked chat')
            # If successful, update the status
            entry["tgGroupJoined"] = "success"
        except errors.UsernameInvalid:
            print(f"Can't find {chat_link}")
            entry["tgGroupJoined"] = "error: Can't find chat"
        except errors.UsernameNotOccupied:
            print(f"Can't find {chat_link}")
            entry["tgGroupJoined"] = "error: Username not occupied"
        except errors.InviteHashExpired:
            print(f"Can't join {chat_link}, link expired")
            entry["tgGroupJoined"] = "error: Invite link expired"
        except Exception as e:
            print(f'Uncaught exception: {e}')
            entry["tgGroupJoined"] = f"error: {e}"

    app.stop()

    # Save the updated results
    with open('bnb_erc20.json', 'w') as f:
        json.dump(data, f, indent=4)

    print('All done!')


if __name__ == '__main__':
    main()
