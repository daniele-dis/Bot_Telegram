import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Carica le variabili dal file .env
load_dotenv() 

# 1. Funzione /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Ciao {update.effective_user.first_name}! Sono il tuo bot. Pronto a ricevere comandi!')

# 2. Funzione eco
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)

# 3. Definizione della funzione di gestione del comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Comandi disponibili:\n"
        "/start - Avvia il bot e ricevi un saluto.\n"
        "/help - Mostra questo messaggio di aiuto.\n"
        "\n"
        "Qualsiasi altro messaggio di testo verrà semplicemente ripetuto (funzione eco)."
    )
    await update.message.reply_text(help_text)

def main() -> None:
    # Recupera il token da .env
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") 
    
    if not TOKEN:
        # Questo errore apparirà se non hai il file .env o il token non è inserito
        raise ValueError("Token non trovato. Verifica il file .env.")

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    #HANDLER per /help
    application.add_handler(CommandHandler("help", help_command))

    #HANDLER per echo
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot avviato e in ascolto...")
    application.run_polling(poll_interval=3)

if __name__ == '__main__':
    main()