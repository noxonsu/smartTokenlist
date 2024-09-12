import json
filename = 'activity-2024-04-02-2024-09-12.json'
cost_per_token = {
    # Стоимость одного токена для каждой модели (стоимость разделена на 1_000_000)
    "chatgpt-4o-latest": {"input": 5.0 / 1_000_000, "output": 15.0 / 1_000_000},
    "gpt-4-turbo": {"input": 10.0 / 1_000_000, "output": 30.0 / 1_000_000},
    "gpt-4-turbo-2024-04-09": {"input": 10.0 / 1_000_000, "output": 30.0 / 1_000_000},
    "gpt-4": {"input": 30.0 / 1_000_000, "output": 60.0 / 1_000_000},
    "gpt-4-0613": {"input": 30.0 / 1_000_000, "output": 60.0 / 1_000_000},
    "gpt-4-32k": {"input": 60.0 / 1_000_000, "output": 120.0 / 1_000_000},
    "gpt-4-0125-preview": {"input": 10.0 / 1_000_000, "output": 30.0 / 1_000_000},
    "gpt-4-1106-preview": {"input": 10.0 / 1_000_000, "output": 30.0 / 1_000_000},
    "gpt-4-vision-preview": {"input": 10.0 / 1_000_000, "output": 30.0 / 1_000_000},
    "gpt-3.5-turbo-0125": {"input": 0.50 / 1_000_000, "output": 1.50 / 1_000_000},
    "gpt-3.5-turbo-instruct": {"input": 1.50 / 1_000_000, "output": 2.00 / 1_000_000},
    "gpt-3.5-turbo-1106": {"input": 1.00 / 1_000_000, "output": 2.00 / 1_000_000},
    "gpt-3.5-turbo-0613": {"input": 1.50 / 1_000_000, "output": 2.00 / 1_000_000},
    "gpt-3.5-turbo-16k-0613": {"input": 3.00 / 1_000_000, "output": 4.00 / 1_000_000},
    "gpt-3.5-turbo-0301": {"input": 1.50 / 1_000_000, "output": 2.00 / 1_000_000},
    "davinci-002": {"input": 2.00 / 1_000_000, "output": 2.00 / 1_000_000},
    "babbage-002": {"input": 0.40 / 1_000_000, "output": 0.40 / 1_000_000},
    "gpt-4o": {"input": 5.0 / 1_000_000, "output": 15.0 / 1_000_000},
    "gpt-4o-2024-08-06": {"input": 2.5 / 1_000_000, "output": 10.0 / 1_000_000},
    "gpt-4o-2024-05-13": {"input": 5.0 / 1_000_000, "output": 15.0 / 1_000_000}
}

# Загрузим JSON файл
with open(filename) as file:
    data = json.load(file)

# Словарь для хранения сумм по API ключам и моделям
expenses = {}
tokens = {}
requests = {}

# Список для неизвестных моделей
unknown_models = []

# Обработка данных
for entry in data['data']:
    api_key_id = entry['api_key_id']
    
    # Пропуск записей с api_key_id 'Playground'
    if api_key_id == 'Playground':
        continue
    
    api_key = entry['api_key_name']
    
    # Замена 'ildario' на 'ildario kura'
    if api_key == 'ildario':
        api_key = 'ildario kura'
    
    model = entry['model']
    
    # Расчёт количества токенов
    n_context_tokens = entry['n_context_tokens_total']
    n_generated_tokens = entry['n_generated_tokens_total']
    total_tokens = n_context_tokens + n_generated_tokens
    
    # Расчёт затрат (учитываем стоимость токенов для каждой модели)
    if model in cost_per_token:
        cost = (n_context_tokens * cost_per_token[model]["input"]) + (n_generated_tokens * cost_per_token[model]["output"])
    else:
        # Если модель не найдена в справочнике, добавляем её в список неизвестных моделей и пропускаем
        unknown_models.append(model)
        continue

    # Сохранение количества запросов
    num_requests = entry.get('num_requests', 1)  # Дефолтное значение запросов – 1, если поле отсутствует
    
    # Инициализация вложенных словарей
    if api_key not in expenses:
        expenses[api_key] = {}
        tokens[api_key] = {}
        requests[api_key] = {}

    if model not in expenses[api_key]:
        expenses[api_key][model] = 0
        tokens[api_key][model] = 0
        requests[api_key][model] = 0
    
    # Сохранение данных
    expenses[api_key][model] += cost
    tokens[api_key][model] += total_tokens
    requests[api_key][model] += num_requests

# Печать результатов (с сортировкой)
sorted_expenses = sorted(expenses.items(), key=lambda x: -sum(x[1].values()))  # сортировка по убыванию затрат

for api_key, model_data in sorted_expenses:
    #print filename and api_key
    print(f"Filename: {filename}")
    print(f"API Key: {api_key}")
    sorted_models = sorted(model_data.items(), key=lambda x: -x[1])  # сортировка моделей по убыванию затрат
    for model, cost in sorted_models:
        print(f"  Model: {model}")
        print(f"    Total Costs on this model: ${cost:.2f}")
        print(f"    Total Tokens: {tokens[api_key][model]}")
        print(f"    Total Requests: {requests[api_key][model]}")
    
    print("total spent: $", sum(model_data.values()))

# Печать неизвестных моделей
if unknown_models:
    print("\nНеизвестные модели:")
    for model in set(unknown_models):  # Используем set() для уникальности
        print(model)