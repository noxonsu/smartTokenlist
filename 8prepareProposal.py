import json
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import os

def load_summary(contract_address):
    filename = os.path.join('summaries', f"{contract_address}.json")
    with open(filename, 'r') as file:
        return json.load(file)['summary']

def load_system_message(filename):
    with open(filename, 'r') as file:
        return file.read()

def generate_message(targetSummary):
    chat = ChatOpenAI(temperature=0.5, model_name="gpt-4")
    system_message_content = load_system_message('GPT_proposal.txt')
    messages = [
        SystemMessage(content=system_message_content),
        HumanMessage(content=f"Target project (this is not our project! analyse them to create an icebreaker and good offer): {targetSummary}")
    ]
    gpttitle = chat(messages)
    return gpttitle.content

def main():
    contract_addresses = [...]  # List of contract addresses
    for contract_address in contract_addresses:
        targetSummary = load_summary(contract_address)
        proposal = generate_message(targetSummary)
        if proposal:
            print(proposal)

if __name__ == "__main__":
    main()
