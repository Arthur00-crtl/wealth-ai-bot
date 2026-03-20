import os
import telebot
import requests
import google.generativeai as genai

# 1. Configuração das Chaves (Lendo EXATAMENTE os nomes da sua Foto 111)
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
            name = data['results'][0].get('longName', ticker)
            return f"O preço de {name} agora é R$ {price:,.2f}"
        return "Ativo não encontrado. Tente PETR4 ou BTC-BRL."
    except Exception as e:
        return "Erro ao acessar dados do mercado."

# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Wealth AI Ativado! 💰\nArthur, vamos buscar esse milhão. Pergunte o preço de uma ação ou peça uma análise.")

# Comando para preços
@bot.message_handler(func=lambda m: 'preço' in m.text.lower())
def handle_price(message):
    text = message.text.upper().replace('PREÇO', '').replace('DO', '').strip()
    result = get_stock_price(text)
    bot.reply_to(message, result)

# Resposta Geral com Gemini
@bot.message_handler(func=lambda m: True)
def ai_response(message):
    prompt = f"Você é o assistente financeiro do Arthur. Ajude-o no plano do milhão: {message.text}"
    try:
        response = model.generate_content(prompt)
        bot.reply_to(message, response.text)
    except:
        bot.reply_to(message, "Estou analisando os dados, tente novamente em breve.")

# Rodar o bot
print("Bot iniciado com sucesso!")
bot.infinity_polling()
