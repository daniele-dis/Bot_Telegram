import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Abbiamo qui tutte le funzioni per l'interfacciamento con l'utente tramite Telegram, anche la funzione echo
# che alla fine sempre di interfacciamento è.

# Importiamo le tue funzioni originali dagli altri file
from monthly_expenses import salva_spesa, get_totale_mese, mostra_report, cancella_ultima_spesa
from weather import get_weather

# Prende la stringa "123,456" dal .env e la trasforma in una lista di numeri [123, 456]
ALLOWED_USERS = [int(i) for i in os.getenv("ALLOWED_USERS", "").split(",") if i.strip()]

# ----- Definiamo dove salvare le foto
BASE_SAVE_PATH = "foto_utenti"

def prepara_cartelle(allowed_users):
    if not os.path.exists(BASE_SAVE_PATH):
        os.makedirs(BASE_SAVE_PATH)
    
    for user_id in allowed_users:
        user_path = os.path.join(BASE_SAVE_PATH, str(user_id))
        if not os.path.exists(user_path):
            os.makedirs(user_path)
            print(f"Cartella creata per l'utente {user_id}")

# Richiama questa funzione all'avvio del bot
prepara_cartelle(ALLOWED_USERS)
# -----

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tasti = [
        ["Chi sei? 🤖", "Che ore sono? 🕒"],
        ["Meteo 🌤️", "Aiuto ❓"],
        ["Spesa 💰", "Report Spese 📊"],
        ["Salva Foto 📸", "Annulla Ultima 🔙"]
    ]
    menu = ReplyKeyboardMarkup(tasti, resize_keyboard=True)
    await update.message.reply_text(
        f'Ciao {update.effective_user.first_name}!👋\nCosa desideri fare?',
        reply_markup=menu
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "<b>🤖 Comandi Disponibili</b>\n\n"
        "🔹 /start - Torna al menu principale\n"
        "🔹 /help - Mostra questa lista comandi\n"
    )
    await update.message.reply_text(
        help_text, 
        parse_mode="HTML", 
        reply_markup=ReplyKeyboardRemove()
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    testo_ricevuto = update.message.text
    u_data = context.user_data
    user_id = update.effective_user.id

    # CONTROLLO SICUREZZA
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("Spiacente, questo bot è privato. 🤐")
        return
    
    if testo_ricevuto.lower() in ["annulla", "esci", "stop"]:
        u_data['attendo_spesa'] = False
        u_data['attendo_citta'] = False
        await update.message.reply_text("Operazione annullata. Torniamo al menu!")
        return

    if testo_ricevuto == "Chi sei? 🤖":
        await update.message.reply_text("Sono il tuo assistente Python! 💻")
        return
    elif testo_ricevuto == "Che ore sono? 🕒":
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
        await update.message.reply_text("Scrivimi: importo descrizione (es: 45,00 Spesa Supermercato)")
        return
    elif testo_ricevuto == "Report Spese 📊":
        await mostra_report(update, context)
        return
    elif testo_ricevuto == "Annulla Ultima 🔙":
        successo, messaggio = cancella_ultima_spesa(user_id)
        await update.message.reply_text(messaggio)
        return
    elif testo_ricevuto == "Aiuto ❓":
        await help_command(update, context)
        return
    elif testo_ricevuto == "Salva Foto 📸":
            await update.message.reply_text(
                "Per salvare una foto nella tua cartella privata, "
                "inviamela direttamente come immagine (non come file)!"
            )
            return

    if u_data.get('attendo_spesa'):
        try:
            testo = testo_ricevuto.strip()
            parti = testo.split(None, 1)
            if len(parti) < 2:
                await update.message.reply_text("Manca la descrizione! Scrivi: 45,00 Regalo")
                return
            cifra_testo = parti[0].replace(',', '.')
            importo = float(cifra_testo)
            descrizione = parti[1]
            salva_spesa(update.effective_user.id, importo, descrizione)
            totale = get_totale_mese(update.effective_user.id)
            u_data['attendo_spesa'] = False # Chiudiamo lo stato solo se è andata bene
            await update.message.reply_text(f"✅ Segnato: {importo:.2f}€ per '{descrizione}'\n💰 Totale mese: {totale:.2f}€")
            
        except Exception:
            # Se c'è un errore, NON settiamo False. L'utente resta in "attendo_spesa"
            await update.message.reply_text(
                "❌ Errore nel formato!\n"
                "-Inserisci nuovamente l'importo e la descrizione.\n"
                "Esempio: 10.50 Pranzo\n\n"
                "Oppure scrivi 'annulla' per tornare al menu."
            )
        return

    if u_data.get('attendo_citta'):
        risposta_meteo = await get_weather(testo_ricevuto)
        await update.message.reply_text(risposta_meteo)
        u_data['attendo_citta'] = False
        return

    await update.message.reply_text(f"Hai scritto: {testo_ricevuto}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id not in ALLOWED_USERS:
        return

    # Prendiamo l'ID della foto con la risoluzione migliore
    photo_file = update.message.photo[-1]
    # Salviamo l'ID del file temporaneamente nei dati utente
    context.user_data['last_photo_id'] = photo_file.file_id

    # Creiamo i bottoni di conferma
    keyboard = [
        [
            InlineKeyboardButton("✅ Salva", callback_data="save_photo"),
            InlineKeyboardButton("❌ Scarta", callback_data="discard_photo"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Ho ricevuto la foto! Vuoi salvarla nella tua cartella personale?",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer() # Importante per togliere l'icona del caricamento sul tasto
    
    user_id = update.effective_user.id
    data = query.data

    if data == "save_photo":
        file_id = context.user_data.get('last_photo_id')
        if file_id:
            # Scarichiamo il file
            new_file = await context.bot.get_file(file_id)
            
            # Generiamo un nome file basato sulla data e ora
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"foto_{timestamp}.jpg"
            save_path = os.path.join(BASE_SAVE_PATH, str(user_id), file_name)
            
            await new_file.download_to_drive(save_path)
            await query.edit_message_text(f"✅ Foto salvata con successo in: {file_name}")
        else:
            await query.edit_message_text("⚠️ Errore: non trovo più la foto.")
            
    elif data == "discard_photo":
        await query.edit_message_text("🗑️ Foto scartata.")
