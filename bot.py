import os
from dotenv import load_dotenv
load_dotenv()
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers import start, help_command, echo


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

    # da qui richiamo le funzioni start, help_command ed echo presenti nell'handler.py
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("BotProvaDani avviato correttamente...")
    application.run_polling()

if __name__ == '__main__':
    main()