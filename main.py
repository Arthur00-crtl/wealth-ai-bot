import os
import time
import threading
import schedule
import telebot
from google import genai
from ddgs import DDGS

TOKEN_TELEGRAM = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('AI_INTEGRATIONS_GEMINI_API_KEY')
GEMINI_BASE_URL = os.environ.get('AI_INTEGRATIONS_GEMINI_BASE_URL')
CHAT_ID_ENV    = os.environ.get('CHAT_ID')

MIN_LINHAS = 2
MAX_LINHAS = 2

if GEMINI_BASE_URL:
    client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options={'base_url': GEMINI_BASE_URL, 'api_version': ''}
    )
else:
    client = genai.Client(api_key=GEMINI_API_KEY)

bot = telebot.TeleBot(TOKEN_TELEGRAM)

chat_ids_ativos: set = set()
if CHAT_ID_ENV:
    chat_ids_ativos.add(int(CHAT_ID_ENV))
chat_ids_lock = threading.Lock()

SYSTEM_PROMPT = (
    "Você é o Wealth AI, assistente financeiro pessoal do Arthur. "
    "Ajude-o a se tornar milionário em 4 anos. "
    "Seja direto, prático e motivador. Responda em português do Brasil."
)

ATIVOS = [
    {"nome": "Bitcoin",     "ticker": "BTC",    "busca": "Bitcoin BTC price USD BRL today variation"},
    {"nome": "Bradesco",    "ticker": "BBDC4",  "busca": "BBDC4 Bradesco ação cotação hoje bolsa B3 variação"},
    {"nome": "Itaú",        "ticker": "ITUB4",  "busca": "ITUB4 Itaú Unibanco ação cotação hoje bolsa B3 variação"},
    {"nome": "Vale",        "ticker": "VALE3",  "busca": "VALE3 Vale ação cotação hoje bolsa B3 variação"},
    {"nome": "BTG Pactual", "ticker": "BPAC11", "busca": "BPAC11 BTG Pactual ação cotação hoje bolsa B3 variação"},
    {"nome": "Apple",       "ticker": "AAPL",   "busca": "AAPL Apple stock price today NASDAQ variation"},
]

PRICE_KEYWORDS = [
    'preço', 'cotação', 'quanto vale', 'quanto está', 'valor', 'bitcoin', 'btc',
    'eth', 'ethereum', 'crypto', 'cripto', 'ação', 'ações', 'bolsa', 'ibovespa',
    'petr', 'vale', 'itub', 'bbdc', 'bpac', 'btg', 'aapl', 'apple', 'nasdaq',
    'dólar', 'dolar', 'euro', 'hoje', 'agora', 'atual'
]


def registrar_chat(chat_id: int):
    with chat_ids_lock:
        if chat_id not in chat_ids_ativos:
            chat_ids_ativos.add(chat_id)
            print(f"[chat] Chat ID registrado: {chat_id}")


def buscar(query: str, n: int = 5) -> str:
    try:
        with DDGS() as ddgs:
            resultados = list(ddgs.text(query, max_results=n))
        return "\n".join(f"- {r.get('title','')}: {r.get('body','')}" for r in resultados)
    except Exception as e:
        print(f"[busca] Erro: {e}")
        return ""


def gemini_call(prompt: str) -> str:
    try:
        r = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return r.text.strip()
    except Exception as e:
        print(f"[gemini] Erro: {e}")
        return "Dados indisponíveis no momento."


def ajustar_linhas(texto: str, minimo: int = MIN_LINHAS, maximo: int = MAX_LINHAS) -> str:
    linhas = [l for l in texto.strip().splitlines() if l.strip()]
    while len(linhas) < minimo:
        linhas.append(linhas[-1] if linhas else "—")
    return "\n".join(linhas[:maximo])


def gerar_mensagem_ativo(nome: str, ticker: str, busca_query: str) -> str:
    dados    = buscar(busca_query, n=6)
    noticias = buscar(f"{nome} {ticker} noticias fundamentos economia hoje", n=4)

    preco = gemini_call(
        f"Baseado nos dados abaixo sobre {nome} ({ticker}), retorne SOMENTE uma linha:\n"
        f"🚀 *{nome}* ({ticker}) | 💰 [preço em R$ ou USD] | 📊 [variação% hoje]\n"
        f"Use '~' se incerto. Sem texto extra.\nDados:\n{dados}"
    )

    noticia = ajustar_linhas(gemini_call(
        f"Sobre {nome} ({ticker}) hoje: escreva EXATAMENTE 2 frases ultra curtas (máx 8 palavras cada). "
        f"Linha 1: variação e motivo. Linha 2: impacto ou contexto. "
        f"SEM título, SEM numeração, SEM texto extra.\nDados:\n{dados}\n{noticias}"
    ))

    insight = ajustar_linhas(gemini_call(
        f"Estratégia para {nome} ({ticker}) no plano do milhão em 4 anos: "
        f"escreva EXATAMENTE 2 frases ultra curtas (máx 8 palavras cada). "
        f"Linha 1: comprar/aguardar e % do portfólio. Linha 2: ação desta semana. "
        f"SEM título, SEM numeração, SEM texto extra.\nDados:\n{dados}"
    ))

    msg = (
        f"📈 *WEALTH AI — {ticker}*\n"
        f"{'—' * 22}\n"
        f"{preco}\n\n"
        f"📰 *NOTÍCIA:*\n{noticia}\n\n"
        f"🤖 *WEALTH AI INSIGHT:*\n{insight}"
    )
    return msg[:4000]


def ciclo_alertas(destinos: set = None):
    with chat_ids_lock:
        alvos = set(destinos) if destinos else set(chat_ids_ativos)

    if not alvos:
        print("[alertas] Nenhum chat registrado. Envie /start para o bot.")
        return

    print(f"[alertas] Iniciando ciclo — {len(ATIVOS)} ativos para {len(alvos)} chat(s)")

    for ativo in ATIVOS:
        try:
            print(f"[alertas] Gerando {ativo['ticker']}...")
            msg = gerar_mensagem_ativo(ativo['nome'], ativo['ticker'], ativo['busca'])
            for cid in alvos:
                try:
                    bot.send_message(cid, msg, parse_mode='Markdown')
                except Exception as e:
                    print(f"[alertas] Erro ao enviar {ativo['ticker']} para {cid}: {e}")
            time.sleep(3)
            print(f"[alertas] {ativo['ticker']} enviado.")
        except Exception as e:
            print(f"[alertas] Erro ao gerar {ativo['ticker']}: {e}")

    print("[alertas] Ciclo concluído.")


def keep_alive():
    try:
        bot.get_me()
        print("[keep-alive] Sinal enviado — bot ativo.")
    except Exception as e:
        print(f"[keep-alive] Erro: {e}")


def rodar_scheduler():
    schedule.every(15).minutes.do(
        lambda: threading.Thread(target=ciclo_alertas, daemon=True).start()
    )
    schedule.every(10).minutes.do(keep_alive)
    while True:
        schedule.run_pending()
        time.sleep(10)


def precisa_busca(texto: str) -> bool:
    return any(kw in texto.lower() for kw in PRICE_KEYWORDS)


@bot.message_handler(commands=['start'])
def cmd_start(message):
    registrar_chat(message.chat.id)
    bot.reply_to(
        message,
        "💰 *Wealth AI Online!*\n\n"
        "✅ Alertas automáticos a cada 15 min\n"
        "✅ Ativos: BTC · BBDC4 · ITUB4 · VALE3 · BPAC11 · AAPL\n"
        "✅ Busca em tempo real ativa\n\n"
        "Comandos:\n"
        "/alerta — dispara todos os alertas agora\n"
        "/status — verifica se o bot está operacional\n\n"
        "Ou me pergunte qualquer coisa sobre finanças!",
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['status'])
def cmd_status(message):
    registrar_chat(message.chat.id)
    bot.reply_to(message, "Wealth AI Operacional! 🚀 Plano do Milhão em andamento.")


@bot.message_handler(commands=['alerta'])
def cmd_alerta(message):
    registrar_chat(message.chat.id)
    bot.reply_to(message, "⏳ Gerando alertas para todos os ativos, aguarde...")
    threading.Thread(
        target=ciclo_alertas,
        kwargs={"destinos": {message.chat.id}},
        daemon=True
    ).start()


@bot.message_handler(func=lambda m: True)
def handle_message(message):
    registrar_chat(message.chat.id)
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        contexto = ""
        if precisa_busca(message.text):
            dados = buscar(f"{message.text} preço hoje", n=4)
            if dados:
                contexto = f"\n\n[Dados da web]\n{dados}"
        prompt = f"{SYSTEM_PROMPT}{contexto}\n\nUsuário: {message.text}"
        resposta = gemini_call(prompt)
        bot.reply_to(message, resposta)
    except Exception as e:
        bot.reply_to(message, f"Erro: {str(e)}")


print("Wealth AI Bot iniciado — alertas: BTC · BBDC4 · ITUB4 · VALE3 · BPAC11 · AAPL")
print("Aguardando usuário enviar /start para registrar Chat ID...")

threading.Thread(target=rodar_scheduler, daemon=True).start()
bot.infinity_polling()
