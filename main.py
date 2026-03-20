import os
import telebot
import requests
import google.generativeai as genai

# 1. Configuração das Chaves
FICHA = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
BRAPI_TOKEN = os.getenv('BRAPI_TOKEN')

# Configurando o Gemini
genai.configure(api_key=GEMINI_KEY)
modelo = genai.GenerativeModel('gemini-pro')

robo = telebot.TeleBot(FICHA)

# Função para buscar preço na Brapi
def buscar_preco(ticker):
    ticker = ticker.upper()
    if ticker in ["BTC", "BITCOIN"]:
        ticker = "BTC-BRL"
    
    url = f"https://brapi.dev/api/quote/{ticker}?token={BRAPI_TOKEN}"
    
    try:
        resposta = requests.get(url)
        dados = resposta.json()
        if "results" in dados:
            preco = dados['results'][0]['regularMarketPrice']
            nome = dados['results'][0].get('longName', ticker)
            return f"O preço de {nome} agora é R$ {preco:,.2f}"
        return "Ativo não encontrado. Tente PETR4 ou BTC-BRL."
    except:
        return "Erro ao acessar dados do mercado."

# Comando /start
@robo.message_handler(commands=['start'])
def boas_vindas(mensagem):
    robo.reply_to(mensagem, "Wealth AI Ativado! 💰\nArthur, vamos buscar esse milhão. Pergunte o preço de uma ação ou peça uma análise.")

# Comando para preços
@robo.message_handler(func=lambda m: 'preço' in m.text.lower())
def lidar_preco(mensagem):
    texto = mensagem.text.upper().replace('PREÇO', '').replace('DO', '').strip()
    resultado = buscar_preco(texto)
    robo.reply_to(mensagem, resultado)

# Resposta Geral com Gemini
@robo.message_handler(func=lambda m: True)
def resposta_ia(mensagem):
    prompt = f"Você é o assistente financeiro do Arthur. Ajude-o no plano do milhão: {mensagem.text}"
    try:
        resultado_ia = modelo.generate_content(prompt)
        robo.reply_to(mensagem, resultado_ia.text)
    except:
        robo.reply_to(mensagem, "Estou analisando os dados, tente novamente em breve.")

# Rodar o bot
print("Bot iniciado com sucesso!")
robo.infinity_polling()
