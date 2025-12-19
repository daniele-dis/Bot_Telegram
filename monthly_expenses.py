import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

def salva_spesa(user_id, importo, descrizione):
    file_path = f"spese_{user_id}.json"
    data_oggi = datetime.now().strftime("%Y-%m-%d")
    mese_corrente = datetime.now().strftime("%Y-%m")
    
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

async def invia_report_mensile(context: ContextTypes.DEFAULT_TYPE):
    user_id = int(os.getenv("MY_TELEGRAM_ID")) 
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

    totale = sum(item['importo'] for item in lista_spese)
    ultime_spese = lista_spese[-5:]

    report_testo = f"📊 **REPORT MENSILE ({mese_corrente})**\n\n"
    for s in ultime_spese:
        report_testo += f"🔹 {s['data']}: {s['importo']:.2f}€ - {s['descrizione']}\n"
    
    report_testo += f"\n💰 **TOTALE SPESO: {totale:.2f}€**"
    
    await update.message.reply_text(report_testo, parse_mode="Markdown")