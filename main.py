import os
import telebot
import google.generativeai as generative_ai

# Configurações do Render
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# Configura o Gemini sem usar o apelido "genai"
generative_ai.configure(api_key=GEMINI_KEY)
model=generative_ai.GenerativeModel('gemini-1.5-flash-latest')

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Wealth AI Ativado! 💰 Arthur, agora o motor está ligado. O que vamos analisar?")

@bot.message_handler(func=lambda m: True)
def ai_response(message):
    try:
        # Usa o modelo configurado acima
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Erro: {e}")
        bot.reply_to(message, "Estou processando os dados... tente de novo!")

bot.infinity_polling()
