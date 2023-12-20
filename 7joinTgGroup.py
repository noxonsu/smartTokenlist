import os
import re
import json
from time import sleep

from pyrogram import Client, errors, types
import random
TELEGRAM_API_ID = int(os.environ.get('TELEGRAM_API_ID'))
TELEGRAM_API_HASH = os.environ.get('TELEGRAM_API_HASH')
MAINFILE = os.environ.get("MAINFILE")
print(TELEGRAM_API_ID)

SUBSCRIBE_TO_LINKED_CHAT = 'true'

def load_and_filter_chats():
    with open(MAINFILE, 'r') as f:
        data = json.load(f)
        # Filtering based on given conditions
        return data, [
            entry for entry in data
            if "web_domains" in entry and entry["web_domains"] 
            and "telegram_groups" in entry and entry["telegram_groups"]
            and "p6" in entry and entry["p6"]
            and "tgGroupJoined" not in entry
        ]
    
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

        count = app.get_chat_members_count(chat_link)
        
        if count > 1000:
            raise ValueError('Chat is too large'+str(count))
        
        chat = app.join_chat(chat_link)

        print(chat)
        
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




def main():
    data, chats_to_subscribe = load_and_filter_chats()
    print(f"Found {len(chats_to_subscribe)} chats to subscribe to")

    # Limit to processing only 6 groups
    chats_to_subscribe = chats_to_subscribe[:10]
    TELEGRAM_SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
    
    

    if TELEGRAM_SESSION_STRING is None:
        app = Client("TgSession", in_memory=True, api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH)
        app.start()
        print("save TELEGRAM_SESSION_STRING="+app.export_session_string())
        return False

    #rand select TELEGRAM_SESSION_STRING or TELEGRAM_SESSION_STRING2 
    if random.randint(0, 1) == 0:
        TELEGRAM_SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
    else:
        TELEGRAM_SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING2')
        
    app = Client('TgSession', session_string=TELEGRAM_SESSION_STRING, api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH)
    print('Bot starting...')
    app.start()
    me = app.get_me()
    print(f'Bot started as {me.username}')
    print('Bot successfully started!')  
    
    for entry in chats_to_subscribe:
        chat_link = entry["telegram_groups"][0]
        try:
            entry["myuser"] = me.id
            # If successful, update the status
            

            chat = subscribe_to_chat_with_retries(app, chat_link)
            if SUBSCRIBE_TO_LINKED_CHAT and chat.type.value != "supergroup" and chat.type.value != "group":
                linked_chat = chat.linked_chat
                if linked_chat:
                    chat = subscribe_to_chat_with_retries(app, linked_chat.id, linked=True)
                    entry["telegram_groups"][0] = linked_chat.username
                else:
                    print('No linked chat')
            
            

            if chat and (not chat.permissions or not chat.permissions.can_send_messages):
                print(f"Can't send messages to {chat_link}")
                entry["tgGroupJoined"] = "error: Can't send messages"
                raise Exception("Can't send messages")
            


            
            entry["tgGroupJoined"] = "success"    
            sleep(3)
            telegram_group = entry["telegram_groups"][0] if entry["telegram_groups"][0] is not None else "Unknown"
            contract_address = entry["contract_address"] if entry["contract_address"] is not None else "Unknown"
            web_domain = entry['web_domains'][0] if entry['web_domains'][0] is not None else "Unknown"

            lastm = "https://t.me/" + telegram_group + " joined " + contract_address + "\n" + web_domain + "\n\n"

            for message in app.get_chat_history(entry["telegram_groups"][0], limit=5):
                if message.text:
                    lastm = lastm + message.text + "\n"
            #if lastm contain "send the solution" or "press the button below"
            if re.search("send the solution", lastm, re.IGNORECASE) or re.search("press the button below", lastm, re.IGNORECASE):
                print("found send the solution or press the button below")
                app.send_message(-1001904539844, text=lastm)
                entry["tgGroupJoined"] = "needhuman"
           
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

        # Save the updated results
        with open(MAINFILE, 'w') as f:
            json.dump(data, f, indent=4)

    app.stop()

    

    print('All done!')


if __name__ == '__main__':
    main()