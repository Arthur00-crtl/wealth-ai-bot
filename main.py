import os
import telebot
import requests
import google.generativeai as genai

# 1. Configuração das Chaves (Lendo do Render)
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
BRAPI_TOKEN = os.getenv('BRAPI_TOKEN')

# Configurando o Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

bot = telebot.TeleBot(TOKEN)

# Função para buscar preço na Brapi
def get_stock_price(ticker):
    ticker = ticker.upper()
    if ticker in ["BTC", "BITCOIN"]:
        ticker = "BTC-BRL"
    url = f"https://brapi.dev/api/quote/{ticker}?token={BRAPI_TOKEN}"
    try:
        response = requests.get(url)
        data = response.json()
        if "results" in data:
            price = data['results'][0]['regularMarketPrice']
            return f"O preço de {ticker} agora é R$ {price:,.2f}"
        return "Ativo não encontrado."
    except:
        return "Erro na consulta."

# Comandos do Telegram
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Wealth AI Online! 💰 Qual o plano para o primeiro milhão hoje?")

@bot.message_handler(func=lambda m: 'preço' in m.text.lower())
def handle_price(message):
    ticker = message.text.upper().replace('PREÇO', '').strip()
    bot.reply_to(message, get_stock_price(ticker))

@bot.message_handler(func=lambda m: True)
def ai_response(message):
    response = model.generate_content(f"Aja como um mentor financeiro para o Arthur: {message.text}")
    bot.reply_to(message, response.text)

# Iniciar
print("Bot Rodando!")
bot.infinity_polling()
