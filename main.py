import os
import telebot
from google import genai

# Configuração lendo do Render
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

client = genai.Client(api_key=GEMINI_KEY)
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Wealth AI Ativado! 💰 Arthur, agora o cérebro está ligado. O que vamos analisar?")

@bot.message_handler(func=lambda m: True)
def ai_response(message):
    try:
        # Nova forma de chamar o Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=message.text
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Erro: {e}")
        bot.reply_to(message, "Ainda ajustando os motores... tente de novo em 10 segundos.")

bot.infinity_polling()
