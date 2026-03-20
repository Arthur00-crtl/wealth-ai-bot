import os
import telebot
import requests
import google.generativeai as genai

# Configuração lendo do Render
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
BRAPI_TOKEN = os.getenv('BRAPI_TOKEN')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Wealth AI Ativado! 💰 Arthur, pronto para buscar o milhão?")

@bot.message_handler(func=lambda m: True)
def ai_response(message):
    try:
        response = model.generate_content(f"Responda ao Arthur: {message.text}")
        bot.reply_to(message, response.text)
    except:
        bot.reply_to(message, "Estou pensando nas estratégias... tente de novo!")

print("Bot Rodando!")
bot.infinity_polling()
