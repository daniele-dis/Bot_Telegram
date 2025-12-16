import os
import requests # ⬅️ Nuova per il meteo
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tasti = [
        ['🤖 Chi sei?', '🕒 Che ore sono?'],
        ['Meteo 🌤️', '❓ Aiuto']
    ]
    menu = ReplyKeyboardMarkup(tasti, resize_keyboard=True)
    
    await update.message.reply_text(
        f'Ciao {update.effective_user.first_name}! Cosa desideri fare?',
        reply_markup=menu
    )

async def get_weather(city_name):
    try:
        # Codifichiamo il nome della città per gestire gli spazi (es. San Giorgio a Cremano)
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
            # Impostiamo uno "stato" temporaneo per dire al bot di aspettare una città
            context.user_data['attendo_citta'] = True
            await update.message.reply_text("Ok! Scrivimi pure il nome della città.")

    elif testo_ricevuto == "❓ Aiuto":
            await help_command(update, context)
        
    else:
            # Se l'utente aveva cliccato su Meteo poco prima
            if context.user_data.get('attendo_citta'):
                risposta_meteo = await get_weather(testo_ricevuto)
                await update.message.reply_text(risposta_meteo)
                # Rimuoviamo lo stato così il bot torna a fare eco normale
                context.user_data['attendo_citta'] = False
            else:
                await update.message.reply_text(f"Hai scritto: {testo_ricevuto}\n(Premi 'Meteo 🌤️' se vuoi conoscere la temperatura di una città!)")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Usa i bottoni o scrivimi il nome di una città per il meteo!")

def main() -> None:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("BotProvaDani avviato...")
    application.run_polling()

if __name__ == '__main__':
    main()