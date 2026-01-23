import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Importiamo le tue funzioni originali dagli altri file
from monthly_expenses import salva_spesa, get_totale_mese, mostra_report, cancella_ultima_spesa
from weather import get_weather
from photo_manager import prepara_cartelle, salva_foto_disco
from shopping import cerca_prezzi
from ai_brain import chiedi_a_gemini

# Prende la stringa "123,456" dal .env e la trasforma in una lista di numeri [123, 456]
ALLOWED_USERS = [int(i) for i in os.getenv("ALLOWED_USERS", "").split(",") if i.strip()]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tasti = [
                ["Chi sei? 🤖", "Chiedi all'IA 🧠"],
                ["Meteo 🌤️", "Cerca Prezzi 🔍"],
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

    # 1. CONTROLLO SICUREZZA
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("Spiacente, questo bot è privato. 🤐")
        return
    
    # 2. COMANDI DI USCITA (Resettano tutto)
    if testo_ricevuto.lower() in ["annulla", "esci", "stop"]:
        u_data['attendo_spesa'] = False
        u_data['attendo_citta'] = False
        u_data['attendo_ai'] = False
        u_data['attendo_prodotto'] = False
        await update.message.reply_text("Operazione annullata. Torniamo al menu!")
        return

    # 3. CONTROLLO PULSANTI MENU (Priorità Assoluta)
    # Se l'utente preme un tasto, resettiamo 'attendo_ai' così non consumiamo quota
    if testo_ricevuto == "Chi sei? 🤖":
        await update.message.reply_text("Sono il tuo assistente Python! 💻")
        return
    
    elif testo_ricevuto == "Chiedi all'IA 🧠":
        u_data['attendo_ai'] = True
        u_data['attendo_citta'] = False
        u_data['attendo_spesa'] = False
        u_data['attendo_prodotto'] = False
        await update.message.reply_text("Certamente! ✨ Chiedimi pure quello che vuoi.")
        return

    elif testo_ricevuto == "Meteo 🌤️":
        u_data['attendo_ai'] = False # IMPORTANTE: Spegne l'IA se era attiva
        u_data['attendo_citta'] = True
        u_data['attendo_spesa'] = False
        await update.message.reply_text("Ok! Scrivimi il nome della città.")
        return
    
    elif testo_ricevuto == "Cerca Prezzi 🔍":
        u_data['attendo_ai'] = False
        u_data['attendo_prodotto'] = True
        u_data['attendo_citta'] = False
        await update.message.reply_text("Cosa vuoi cercare? (es: iPhone 15)")
        return

    elif testo_ricevuto == "Spesa 💰":
        u_data['attendo_ai'] = False
        u_data['attendo_spesa'] = True
        u_data['attendo_citta'] = False
        await update.message.reply_text("Scrivimi: importo descrizione (es: 45,00 Spesa)")
        return
    
    elif testo_ricevuto == "Report Spese 📊":
        u_data['attendo_ai'] = False # Se clicchi il report, esci dalla modalità IA
        await mostra_report(update, context)
        return
    
    elif testo_ricevuto == "Annulla Ultima 🔙":
        u_data['attendo_ai'] = False
        successo, messaggio = cancella_ultima_spesa(user_id)
        await update.message.reply_text(messaggio)
        return
    
    elif testo_ricevuto == "Salva Foto 📸":
        await update.message.reply_text("Inviami direttamente l'immagine per salvarla! (No File, Caricala Nella Chat)")
        return

    # 4. GESTIONE STATI (Cosa succede dopo aver premuto i tasti)

    # IA (Se attivo, risponde a tutto il resto)
    if u_data.get('attendo_ai'):
        msg_attesa = await update.message.reply_text("Ci sto pensando... 🤔")
        risposta_vera = await chiedi_a_gemini(testo_ricevuto)
        await msg_attesa.edit_text(risposta_vera, parse_mode="HTML")
        return

    # Cerca Prezzi
    if u_data.get('attendo_prodotto'):
        await update.message.reply_text(f"Sto cercando '{testo_ricevuto}'... ⏳")
        risultato = cerca_prezzi(testo_ricevuto)
        await update.message.reply_text(risultato, parse_mode="HTML", disable_web_page_preview=True)
        u_data['attendo_prodotto'] = False
        return

    # Spesa
    if u_data.get('attendo_spesa'):
        try:
            parti = testo_ricevuto.strip().split(None, 1)
            importo = float(parti[0].replace(',', '.'))
            salva_spesa(user_id, importo, parti[1])
            totale = get_totale_mese(user_id)
            u_data['attendo_spesa'] = False
            await update.message.reply_text(f"✅ Segnato: {importo:.2f}€\n💰 Totale: {totale:.2f}€")
        except:
            await update.message.reply_text("❌ Errore formato! Esempio: 10.50 Pranzo")
        return

    # Meteo
    if u_data.get('attendo_citta'):
        risposta_meteo = await get_weather(testo_ricevuto)
        await update.message.reply_text(risposta_meteo)
        u_data['attendo_citta'] = False
        return

    # 5. RISPOSTA DI DEFAULT (Se non ci sono stati attivi e non è un tasto menu)
    await update.message.reply_text(f"Non ho capito il comando. Usa il menu qui sotto! 👇")


# Richiama questa funzione prima delle funzioni per la gestione delle foto
prepara_cartelle(ALLOWED_USERS)
# -----

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
    await query.answer() # Toglie il caricamento dal tasto
    
    user_id = update.effective_user.id
    data = query.data

    if data == "save_photo":
        file_id = context.user_data.get('last_photo_id')
        if file_id:
            # USIAMO LA FUNZIONE ESTERNA DI PHOTO_MANAGER
            # Passiamo il bot, l'ID utente e l'ID del file
            successo, risultato = await salva_foto_disco(context.bot, user_id, file_id)
            
            if successo:
                # 'risultato' contiene il nome del file in caso di successo
                await query.edit_message_text(f"✅ Foto salvata con successo in: {risultato}")
            else:
                # 'risultato' contiene l'errore in caso di fallimento
                await query.edit_message_text(f"❌ Errore durante il salvataggio: {risultato}")
        else:
            await query.edit_message_text("⚠️ Errore: non trovo più la foto.")
            
    elif data == "discard_photo":
        await query.edit_message_text("🗑️ Foto scartata.")