from playwright.sync_api import sync_playwright
from openai import OpenAI
import os
import base64
from dotenv import load_dotenv
import json
import requests
# Загрузить переменные окружения из .env файла
load_dotenv()

# Установить ключ OpenAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if OPENAI_API_KEY is None or not OPENAI_API_KEY.startswith('sk-'):
	raise ValueError("OpenAI API key is not set or invalid. Make sure to set the 'MY_OPENAI_KEY' environment variable in the .env file.")

TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

client = OpenAI(api_key=OPENAI_API_KEY)

# Использование Playwright для получения скриншота
with sync_playwright() as p:
	browser = p.chromium.launch(headless=True)
	page = browser.new_page()
	page.goto("https://www.coinglass.com/pro/i/RsiHeatMap")
	try:
		page.click('button:has-text("Consent")')  # Замените селектором, который соответствует кнопке.
	except:
		pass
	page.screenshot(path="12trackCoingGlassRSI.png")
	page.click('text="4 hour"')  # Открыть выпадающий список
	page.screenshot(path="12trackCoingGlassRSI11.png")
	page.click('text="15 minute"')  # Выбрать опцию "15 min"
	page.screenshot(path="12trackCoingGlassRSI12.png")
	# Подождать 4 секунды
	page.wait_for_timeout(5000)

# Открытие скриншота и конвертация его в base64
image_path = '12trackCoingGlassRSI12.png'
with open(image_path, 'rb') as image_file:
	image_base64 = base64.b64encode(image_file.read()).decode('utf-8')


print('Image converted to base64 successfully')
#send file to telegram
url = f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto'
files = {'photo': open(image_path, 'rb')}
data = {
	'chat_id': TG_CHAT_ID,
	'caption': 'RSI 12 track'
}
r = requests.post(url, files=files, data=data)


# Запрос к OpenAI с изображением в base64, уточнение задания
response = client.chat.completions.create(
	model='gpt-4o',
	messages=[
		{
			"role": "user",
			"content": [
				{"type": "text", "text": 'Это RSI карта. Определи, какой asset находится в красной области и движется в сторону OVERBOUGHT (или находится в ней) с учетом его хвоста. Хвост - это тонкая линия, опускающаяся от центра маркера вниз. Чем она длиннее, тем лучше, чем левее маркер, тем лучше. Не возвращай ассеты, которые находятся ниже красной области. Относительный вес (лучше или хуже) выражай от 1 до 100 как score. Если на фоне красного нет маркеров, то не возвращай ассеты вообще. Верни результат в массиве JSON (каждый элемент asset_name, score). Пример ответа: "{\"assets\": [{\"asset_name\": \"BNB\", \"score\": 100}]}"'},
				{
					"type": "image_url",
					"image_url": {"url": f"data:image/png;base64,{image_base64}"}
				},
			],
		}
	],
	max_tokens=500,
	response_format={"type": "json_object"}
)
assets = response.choices[0].message.content
links = []  # Initialize the links variable as an empty list
try:
	assets_list = json.loads(assets)

	assets_list = assets_list['assets']  # Получаем список активов из словаря
	if not assets_list:
		raise ValueError("No assets found in the response.")
	
	
	for asset in assets_list:
		asset_name = asset.get('asset_name')
		if asset_name:
			print(f"Asset name: {asset_name}")
			links.append(f'https://www.bybit.com/trade/usdt/{asset_name}USDT')  # Append the link to the links list
		else:
			print("Asset name not found")
except (KeyError, ValueError) as e:
	print(f"Error processing assets: {e}")
	exit(1)
#{
#  "asset_name": "BNB",
#  "segment": "overbought",
#  "score": 100
#}

#open https://www.coinglass.com/currencies/{asset_name} 
with sync_playwright() as p:
	browser = p.chromium.launch(headless=True)
	page = browser.new_page()
	#todo

	  
# Отправка сообщения в Telegram с загрузкой картинки 12trackCoingGlassRSI12.png и текстом assets
import requests
url = f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto'
files = {'photo': open(image_path, 'rb')}
data = {
	'chat_id': TG_CHAT_ID,
	'caption': '\n'.join(links)
}


r = requests.post(url, files=files, data=data)
print(r.json())


