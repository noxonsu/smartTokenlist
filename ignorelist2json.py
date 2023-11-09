import json

def filter_domains_from_json():
    # Загрузить bnb_erc20.json
    with open(MAINFILE, "r", encoding='utf-8') as f:
        existing_data = json.load(f)

    # Загрузить игнорируемые домены из ignoredomains.txt
    with open('ignoredomains.txt', 'r', encoding='utf-8') as file:
        IGNORED_DOMAINS = set(file.read().split(','))

    # Обойти данные для проверки игнорируемых доменов
    for entry in existing_data:
        if 'web_domains' in entry:
            if any(domain in IGNORED_DOMAINS for domain in entry['web_domains']):
                del entry['web_domains']  # Удалить поле web_domains, если любой домен совпадает с игнорируемыми

    # Сохранить измененные данные обратно в bnb_erc20.json
    with open(MAINFILE, "w", encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)

filter_domains_from_json()
