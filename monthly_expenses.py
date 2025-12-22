import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from fpdf import FPDF

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

    # Genera e invia il PDF
    file_pdf = genera_pdf_spese(user_id, mese_corrente)
    if file_pdf:
        with open(file_pdf, "rb") as document:
            await context.bot.send_document(
                chat_id=user_id,
                document=document,
                filename=f"Report_{mese_corrente}.pdf",
                caption="Ecco il tuo report dettagliato in PDF! 📄"
            )
        os.remove(file_pdf) # Rimuove il file dal server dopo averlo inviato
    else:
        await update.message.reply_text("Non ho dati sufficienti per creare un PDF.")
    
    await update.message.reply_text(report_testo, parse_mode="Markdown")

def genera_pdf_spese(user_id, mese_corrente):
    file_json = f"spese_{user_id}.json"
    pdf_filename = f"report_{mese_corrente}_{user_id}.pdf"
    
    if not os.path.exists(file_json):
        return None

    with open(file_json, "r") as f:
        dati = json.load(f)

    spese = dati.get(mese_corrente, [])
    if not spese:
        return None

    # Creazione PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, f"Report Spese - {mese_corrente}", ln=True, align='C')
    pdf.ln(10)

    # Intestazione Tabella
    pdf.set_font("Arial", "B", 12)
    pdf.cell(40, 10, "Data", 1)
    pdf.cell(100, 10, "Descrizione", 1)
    pdf.cell(50, 10, "Importo", 1)
    pdf.ln()

    # Contenuto
    pdf.set_font("Arial", "", 12)
    totale = 0
    for s in spese:
        pdf.cell(40, 10, s['data'], 1)
        pdf.cell(100, 10, s['descrizione'], 1)
        pdf.cell(50, 10, f"{s['importo']:.2f} euro", 1)
        pdf.ln()
        totale += s['importo']

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, f"TOTALE MENSILE: {totale:.2f} euro", align='R')

    pdf.output(pdf_filename)
    return pdf_filename

def cancella_ultima_spesa(user_id):
    file_path = f"spese_{user_id}.json"
    mese_corrente = datetime.now().strftime("%Y-%m")
    
    if not os.path.exists(file_path):
        return False, "Nessun dato trovato."

    with open(file_path, "r") as f:
        spese = json.load(f)

    if mese_corrente in spese and len(spese[mese_corrente]) > 0:
        # Rimuove l'ultimo elemento della lista
        spesa_rimossa = spese[mese_corrente].pop()
        
        with open(file_path, "w") as f:
            json.dump(spese, f, indent=4)
        
        return True, f"Eliminata: {spesa_rimossa['importo']:.2f}€ ({spesa_rimossa['descrizione']})"
    
    return False, "Nessuna spesa da eliminare per questo mese."