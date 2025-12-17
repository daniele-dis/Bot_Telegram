import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
import json

load_dotenv()

# --- FUNZIONI PER IL MONEY TRACKER ---

def salva_spesa(user_id, importo, descrizione):
    file_path = f"spese_{user_id}.json"
    data_oggi = datetime.now().strftime("%Y-%m-%d")
    mese_corrente = datetime.now().strftime("%Y-%m")
    
    # Carichiamo i dati esistenti
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            spese = json.load(f)
    else:
        spese = {}

    if mese_corrente not in spese:
        spese[mese_corrente] = []

    spese[mese_corrente].append({
        "data": data_oggi,
        "importo": float(importo),
        "descrizione": descrizione
    })

    with open(file_path, "w") as f:
        json.dump(spese, f, indent=4)

def get_totale_mese(user_id):
    file_path = f"spese_{user_id}.json"
    mese_corrente = datetime.now().strftime("%Y-%m")
    if not os.path.exists(file_path):
        return 0.0
    
    with open(file_path, "r") as f:
        spese = json.load(f)
    
    totale = sum(item['importo'] for item in spese.get(mese_corrente, []))
    return totale

# --- FUNZIONE PER IL REPORT AUTOMATICO (Ogni 1 del mese) ---

async def invia_report_mensile(context: ContextTypes.DEFAULT_TYPE):
    user_id = 1524019319 # Il tuo ID
    totale = get_totale_mese(user_id)
    messaggio = f"🗓️ **RESOCONTO MENSILE**\n\nNel mese appena concluso hai speso in totale: **{totale:.2f}€**."
    await context.bot.send_message(chat_id=user_id, text=messaggio, parse_mode="HTML")

async def mostra_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    file_path = f"spese_{user_id}.json"
    mese_corrente = datetime.now().strftime("%Y-%m")
    
    if not os.path.exists(file_path):
        await update.message.reply_text("Non hai ancora registrato nessuna spesa! 📭")
        return

    with open(file_path, "r") as f:
        spese = json.load(f)

    lista_spese = spese.get(mese_corrente, [])
    
    if not lista_spese:
        await update.message.reply_text("Nessuna spesa per questo mese. 🤷‍♂️")
        return

    # Calcoliamo il totale e prendiamo le ultime 5
    totale = sum(item['importo'] for item in lista_spese)
    ultime_spese = lista_spese[-5:] # Prende le ultime 5 inserite

    report_testo = f"📊 **REPORT MENSILE ({mese_corrente})**\n\n"
    for s in ultime_spese:
        report_testo += f"🔹 {s['data']}: {s['importo']:.2f}€ - {s['descrizione']}\n"
    
    report_testo += f"\n💰 **TOTALE SPESO: {totale:.2f}€**"
    
    await update.message.reply_text(report_testo, parse_mode="Markdown")

# --- FUNZIONE PER IL MESSAGGIO AUTOMATICO ALL'AVVIO ---
async def post_init(application):
    # Inseriamo l'ID direttamente come numero
    mio_id = 1524019319 
    
    try:
        # Messaggio di avvio nel terminale e su Telegram
        await application.bot.send_message(chat_id=mio_id, text="Ciao, sono BotProvaDani, in cosa posso esserti d'aiuto?😊")
        
        # Mostriamo la lista comandi SOLO all'avvio del file python
        help_text = (
            "<b>🤖 Comandi Disponibili</b>\n\n"
            "/start - Avvia e mostra il menu\n"
            "/help - Mostra questa lista\n"
        )
        await application.bot.send_message(chat_id=mio_id, text=help_text, parse_mode="HTML")
    except Exception as e:
        print(f"Messaggio automatico non inviato (ID non configurato o bot non avviato con l'utente): {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tasti = [
        ['🤖 Chi sei?', '🕒 Che ore sono?'],
        ['Meteo 🌤️', '❓ Aiuto'],
        ['Spesa 💰', '📊 Report Spese']
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
    u_data = context.user_data

    # 1. MENU
    if testo_ricevuto == "🤖 Chi sei?":
        await update.message.reply_text("Sono il tuo assistente Python! 💻")
        return
    elif testo_ricevuto == "🕒 Che ore sono?":
        await update.message.reply_text(f"Sono le {datetime.now().strftime('%H:%M')}!")
        return
    elif testo_ricevuto == "Meteo 🌤️":
        u_data['attendo_citta'] = True
        u_data['attendo_spesa'] = False
        await update.message.reply_text("Ok! Scrivimi il nome della città.")
        return
    elif testo_ricevuto == "Spesa 💰":
        u_data['attendo_spesa'] = True
        u_data['attendo_citta'] = False
        await update.message.reply_text("Scrivimi: importo descrizione (es: 45,00 Regalo Mamma)")
        return
    elif testo_ricevuto == "📊 Report Spese":
        await mostra_report(update, context)
        return
    elif testo_ricevuto == "❓ Aiuto":
        await help_command(update, context)
        return

    # 2. GESTIONE INPUT
    if u_data.get('attendo_spesa'):
        try:
            testo = testo_ricevuto.strip()
            # Usiamo split() senza argomenti per essere più flessibili con gli spazi
            parti = testo.split(None, 1)
            
            if len(parti) < 2:
                await update.message.reply_text("Manca la descrizione! Scrivi: 45,00 Regalo")
                return

            cifra_testo = parti[0].replace(',', '.')
            importo = float(cifra_testo)
            descrizione = parti[1]

            # QUI POTREBBE ESSERCI L'ERRORE VERO
            salva_spesa(update.effective_user.id, importo, descrizione)
            totale = get_totale_mese(update.effective_user.id)
            
            await update.message.reply_text(f"✅ Segnato: {importo:.2f}€ per '{descrizione}'\n💰 Totale mese: {totale:.2f}€")
            u_data['attendo_spesa'] = False
            
        except Exception as e:
            # QUESTO PRINT È FONDAMENTALE: guarda cosa appare nel terminale di VS Code!
            print(f"ERRORE REALE: {e}")
            await update.message.reply_text(f"Errore tecnico. Controlla il terminale o riprova.")
        return

    if u_data.get('attendo_citta'):
        risposta_meteo = await get_weather(testo_ricevuto)
        await update.message.reply_text(risposta_meteo)
        u_data['attendo_citta'] = False
        return

    await update.message.reply_text(f"Hai scritto: {testo_ricevuto}")

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