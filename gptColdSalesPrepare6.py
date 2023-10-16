import json
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import Html2TextTransformer
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_extraction_chain
from langchain.schema import SystemMessage, HumanMessage
import os
from bs4 import BeautifulSoup
import re

def load_data_from_file(filename):
    with open(filename, "r") as f:
        return json.load(f)


def filter_sites_without_summary(data):
    return [(entry['web_domains'][0], entry['contract_address']) for entry in data if not entry.get('processedGpt') and entry.get('web_domains')][:3]




def extract_content(site):
    loader = AsyncChromiumLoader(["https://"+site])
    docs = loader.load()
    
    # Extract Telegram links
    telegram_links = extract_telegram_links(docs[0].page_content)
    print ("telegram_links")
    print (telegram_links)
    # Transform the content to text
    html2text = Html2TextTransformer()
    text_content = html2text.transform_documents(docs)

    return text_content, telegram_links

def extract_telegram_links(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    regex = re.compile(r"https?://t\.me/(\w+)")
    links = soup.find_all('a', href=regex)

    telegram_groups = [regex.search(link['href']).group(1) for link in links]
    return telegram_groups


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

def save_summary_and_proposal(contract_address, summary, proposal):
    """Сохраняет summary и proposal в отдельный файл в папке 'texts'"""
    if not os.path.exists('texts'):
        os.makedirs('texts')  # Создаем папку, если её нет

    filename = os.path.join('texts', f"{contract_address}.json")
    with open(filename, 'w') as file:
        json.dump({
            'summary': summary,
            'proposal': proposal
        }, file, indent=4)


def process_sites(data, sites_without_summary):
    schema = {
        "properties": {
            "news_article_title": {"type": "string"},
            "news_article_summary": {"type": "string"},
        },
        "required": ["news_article_title", "news_article_summary"],
    }

    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")

    for site, contract in sites_without_summary:
        print(f"Analyzing site: {site}")
        print(f"Contract Address: {contract}")

        docs_transformed, telegram_links = extract_content(site)


        # Extract relevant content
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=2000, chunk_overlap=0)
        splits = splitter.split_documents(docs_transformed)
        try:
            extracted_content = create_extraction_chain(schema=schema, llm=llm).run(splits[0].page_content)
            combined_content = [f"{item.get('news_article_title', '')} - {item.get('news_article_summary', '')}\n\n" for item in extracted_content]
            targetSummary = ' '.join(combined_content)

            if targetSummary:
                proposal = generate_message(targetSummary)
            else:
                targetSummary = "None"
                proposal = None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for site {site}: {e}")
            targetSummary = "Failed to extract content due to JSON decoding error"
            proposal = "Extraction failure due to JSON decoding error"

        # Update the data list
        save_summary_and_proposal(contract, targetSummary, proposal)


To ensure that you only add new Telegram groups (without duplicates), you can utilize Python's set functionality.

Here's how you can adjust the process_sites function to accomplish this:

python
Copy code
def process_sites(data, sites_without_summary):
    # ... [rest of the function above this point remains unchanged] ...
    
    for site, contract in sites_without_summary:
        print(f"Analyzing site: {site}")
        print(f"Contract Address: {contract}")

        docs_transformed, telegram_links = extract_content(site)

        # Extract relevant content
        # ... [rest of the function remains unchanged] ...
        
        # Update the data list to include Telegram links
        for entry in data:
            if entry.get('web_domains') and entry['web_domains'][0] == site:
                # Combine existing and new telegram groups, ensuring no duplicates
                existing_telegram_groups = set(entry.get('telegram_groups', []))
                telegram_links = list(existing_telegram_groups.union(telegram_links))
                entry['telegram_groups'] = telegram_links
                entry['processedGpt'] = True



def save_updated_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def main():
    data = load_data_from_file("bnb_erc20.json")
    sites_without_summary = filter_sites_without_summary(data)

    if not sites_without_summary:
        print("All sites processed")
    else:
        process_sites(data, sites_without_summary)
        save_updated_data("bnb_erc20.json", data)


if __name__ == "__main__":
    main()
