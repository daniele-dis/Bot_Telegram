import os
from dotenv import load_dotenv
load_dotenv()
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from handlers import start, help_command, echo, handle_photo, button_handler

# !!! bot.py but this is the MAIN

async def post_init(application):
    mio_id = int(os.getenv("MY_TELEGRAM_ID"))
    try:

        #All'avvio del bot da terminale, questo è quell oche vedo in chat, in modo automatico
        await application.bot.send_message(chat_id=mio_id, text="Ciao, sono BotProvaDani, in cosa posso esserti d'aiuto?😊")
        help_text = (
            "<b>🤖 Comandi Disponibili</b>\n\n"
            "/start - Avvia e mostra il menu\n"
            "/help - Mostra questa lista\n"
        )
        await application.bot.send_message(chat_id=mio_id, text=help_text, parse_mode="HTML")
    except Exception as e:
        print(f"Messaggio automatico non inviato: {e}")

def main() -> None:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    # 1. Comandi slash
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # 2. Gestore FOTO (deve stare prima o insieme ai messaggi di testo)
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # 3. Gestore BOTTONI INLINE (Salva/Scarta)
    application.add_handler(CallbackQueryHandler(button_handler))

    # 4. Gestore TESTO (Echo e logica menu)
    # Importante: questo deve restare per ultimo tra i MessageHandler di testo
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("BotProvaDani avviato correttamente...")
    application.run_polling()

if __name__ == '__main__':
    main()