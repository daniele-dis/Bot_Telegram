
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes

# Abbiamo qui tutte le funzioni per l'interfacciamento con l'utente tramite Telegram, anche la funzione echo
# che alla fine sempre di interfacciamento è.

# Importiamo le tue funzioni originali dagli altri file
from monthly_expenses import salva_spesa, get_totale_mese, mostra_report
from weather import get_weather

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tasti = [
        ['🤖 Chi sei?', '🕒 Che ore sono?'],
        ['Meteo 🌤️', '❓ Aiuto'],
        ['Spesa 💰', '📊 Report Spese']
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
            await update.message.reply_text(f"✅ Segnato: {importo:.2f}€ per '{descrizione}'\n💰 Totale mese: {totale:.2f}€")
            u_data['attendo_spesa'] = False
        except Exception as e:
            print(f"ERRORE REALE: {e}")
            await update.message.reply_text(f"Errore tecnico. Controlla il terminale o riprova.")
        return

    if u_data.get('attendo_citta'):
        risposta_meteo = await get_weather(testo_ricevuto)
        await update.message.reply_text(risposta_meteo)
        u_data['attendo_citta'] = False
        return

    await update.message.reply_text(f"Hai scritto: {testo_ricevuto}")


