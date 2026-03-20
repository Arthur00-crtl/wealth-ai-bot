import os
import telebot
import google.generativeai as genai

# Configuração lendo do Render
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# Conecta o Gemini (Jeito estável)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Wealth AI Ativado! 💰 Arthur, agora o cérebro está ligado. O que vamos analisar?")

@bot.message_handler(func=lambda m: True)
def ai_response(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Erro: {e}")
        bot.reply_to(message, "Estou processando os dados... tente de novo em alguns segundos!")

bot.infinity_polling()
