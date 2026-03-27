import os
import telebot
from openai import OpenAI

# Configurações das Variáveis de Ambiente
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

bot = telebot.TeleBot(TOKEN)

# Configuração do Cliente OpenRouter (Evita o bloqueio regional)
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=OPENROUTER_API_KEY,
)

def get_ai_response(user_input):
    try:
        completion = client.chat.completions.create(
          model="google/gemini-flash-1.5",
          messages=[
            {"role": "system", "content": "Você é o Wealth AI, um assistente especializado em finanças e economia para estudantes."},
            {"role": "user", "content": user_input}
          ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Erro na IA: {e}")
        return "Tive um probleminha para pensar agora. Tente novamente em instantes!"

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    bot.reply_to(message, "Estou analisando... só um momento.")
    response = get_ai_response(message.text)
    bot.send_message(message.chat.id, response)

if __name__ == "__main__":
    print("Wealth AI Online!")
    bot.infinity_polling()
