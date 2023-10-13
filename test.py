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
    return [(entry['web_domains'][0], entry['contract_address']) for entry in data if not entry.get('targetSummary') and entry.get('web_domains')][:2]


def extract_content(site):
    loader = AsyncChromiumLoader([site])
    docs = loader.load()
    html2text = Html2TextTransformer()
    return html2text.transform_documents(docs)


def generate_message(targetSummary):
    chat = ChatOpenAI(temperature=0.5, model_name="gpt-4")
    messages = [
        SystemMessage(content="Help me to create a telegram message to the telegram group of project I send to you. Create icebreaker based of target project summary data! align our B2B tools to their vision. Attract community not team. Lottery and dex are revenue share tools, anyone from the community can deploy. We are a shop of the B2B tools. Use simple english! Use their token ticker if possible. Use neutral emotion (no exiting etc..). Use humor if possible. Use numbers from their project's information if possible. Base proposal:  our primary goal is to support the growth of communities like yours. We have such tool for this: \n\nWant your own DEX? We got a customizable one. 🔄\nFancy launching a blockchain-based lottery? Try ours! \nNeed a multicurrency crypto wallet? Got that too. \nYield farming & staking? All set with our platform. \nCreate a DAO for your token? Check! \nEVM blockchain bridge? CrossChain's got you. \nLaunching an IDO? Our Launchpad is waiting. 🚀\nIt's all B2B, so you're not playing, you're creating. Let me know if interested! 👋\nCheck it out https://t.me/onoutdemos"),
        HumanMessage(content=f"Target project (this is not our project! analyse them to create icebreaker and good offer): {targetSummary}")
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
        }, file)


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
        extracted_content = create_extraction_chain(schema=schema, llm=llm).run(splits[0].page_content)

        # Combine extracted content
        combined_content = [f"{item.get('news_article_title', '')} - {item.get('news_article_summary', '')}\n\n" for item in extracted_content]
        targetSummary = ' '.join(combined_content)

        proposal = None
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
                entry['processed'] = True

        if proposal:
            print(proposal)



def save_updated_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)


def main():
    data = load_data_from_file("bnb_erc20.json")
    sites_without_summary = filter_sites_without_summary(data)

    if not sites_without_summary:
        print("All sites processed")
    else:
        process_sites(data, sites_without_summary)
        save_updated_data("bnb_erc20.jso.json", data)


if __name__ == "__main__":
    main()
