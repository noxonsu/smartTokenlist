import json
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import Html2TextTransformer
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_extraction_chain
from langchain.schema import SystemMessage, HumanMessage
import os

def load_data_from_file(filename):
    with open(filename, "r") as f:
        return json.load(f)


def filter_sites_without_summary(data):
    return [(entry['web_domains'][0], entry['contract_address']) for entry in data if not entry.get('processedGpt') and entry.get('web_domains')][:5]


def extract_content(site):
    loader = AsyncChromiumLoader(["https://"+site])
    docs = loader.load()
    html2text = Html2TextTransformer()
    return html2text.transform_documents(docs)


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

        docs_transformed = extract_content(site)

        # Extract relevant content
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=2000, chunk_overlap=0)
        splits = splitter.split_documents(docs_transformed)
        if not splits:
            print(f"Couldn't extract content from {site}.")
            targetSummary = "Failed to extract content"
            proposal = "Extraction failure"
        else:
            extracted_content = create_extraction_chain(schema=schema, llm=llm).run(splits[0].page_content)
            combined_content = [f"{item.get('news_article_title', '')} - {item.get('news_article_summary', '')}\n\n" for item in extracted_content]
            targetSummary = ' '.join(combined_content)

            if targetSummary:
                proposal = generate_message(targetSummary)
            else:
                targetSummary = "None"
                proposal = None


        # Update the data list
        save_summary_and_proposal(contract, targetSummary, proposal)

        # Update the data list to mark the site as processed
        for entry in data:
            if entry.get('web_domains') and entry['web_domains'][0] == site:
                entry['processedGpt'] = True

        if proposal:
            print(proposal)



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
