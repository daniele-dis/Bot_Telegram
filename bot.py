import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove

load_dotenv()

# --- FUNZIONE PER IL MESSAGGIO AUTOMATICO ALL'AVVIO ---
async def post_init(application):
    # Inseriamo l'ID direttamente come numero
    mio_id = 1524019319 
    
    try:
        # Messaggio di avvio nel terminale e su Telegram
        await application.bot.send_message(chat_id=mio_id, text="🚀 BotProvaDani avviato e pronto su VS Code!")
        
        # Mostriamo la lista comandi SOLO all'avvio del file python
        help_text = (
            "<b>🤖 Comandi Disponibili</b>\n\n"
            "🔹 /start - Avvia e mostra il menu\n"
            "🔹 /help - Mostra questa lista\n"
        )
        await application.bot.send_message(chat_id=mio_id, text=help_text, parse_mode="HTML")
    except Exception as e:
        print(f"Messaggio automatico non inviato (ID non configurato o bot non avviato con l'utente): {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tasti = [
        ['🤖 Chi sei?', '🕒 Che ore sono?'],
        ['Meteo 🌤️', '❓ Aiuto']
    ]
    menu = ReplyKeyboardMarkup(tasti, resize_keyboard=True)
    
    # Ora /start invia SOLO il saluto e i tasti, senza la lista testuale dell'help
    await update.message.reply_text(
        f'Ciao {update.effective_user.first_name}!👋\nCosa desideri fare?',
        reply_markup=menu
    )

async def get_weather(city_name):
    try:
        city_encoded = requests.utils.quote(city_name)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_encoded}&count=1&language=it&format=json"
        geo_res = requests.get(geo_url).json()
        
        if not geo_res.get('results'):
            return f"Mi dispiace, non ho trovato '{city_name}'. Prova a scriverla diversamente."

        data = geo_res['results'][0]
        lat, lon = data['latitude'], data['longitude']
        nome_completo = f"{data['name']} ({data.get('admin1', '')}, {data.get('country', '')})"

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(weather_url).json()
        
        temp = w_res['current_weather']['temperature']
        return f"A {nome_completo} ci sono attualmente {temp}°C. 🌡️"
    except Exception as e:
        print(f"Errore: {e}")
        return "Errore tecnico nel recupero del meteo."

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    testo_ricevuto = update.message.text

    if testo_ricevuto == "🤖 Chi sei?":
        await update.message.reply_text("Sono il tuo assistente Python creato su VS Code! 💻")
    
    elif testo_ricevuto == "🕒 Che ore sono?":
        ora = datetime.now().strftime("%H:%M")
        await update.message.reply_text(f"Sono le {ora}!")

    elif testo_ricevuto == "Meteo 🌤️":
        context.user_data['attendo_citta'] = True
        await update.message.reply_text("Ok! Scrivimi pure il nome della città.")

    elif testo_ricevuto == "❓ Aiuto":
        await help_command(update, context)
        
    else:
        if context.user_data.get('attendo_citta'):
            risposta_meteo = await get_weather(testo_ricevuto)
            await update.message.reply_text(risposta_meteo)
            context.user_data['attendo_citta'] = False
        else:
            await update.message.reply_text(f"Hai scritto: {testo_ricevuto}\n")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "<b>🤖 Comandi Disponibili</b>\n\n"
        "🔹 /start - Torna al menu principale\n"
        "🔹 /help - Mostra questa lista comandi\n"
    )
    
    # Usiamo reply_markup=ReplyKeyboardRemove() per nascondere i bottoni
    await update.message.reply_text(
        help_text, 
        parse_mode="HTML", 
        reply_markup=ReplyKeyboardRemove()
    )

def main() -> None:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Aggiungiamo .post_init(post_init) per il messaggio automatico
    application = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("BotProvaDani avviato correttamente...")
    application.run_polling()

if __name__ == '__main__':
    main()