import os
import asyncio
from datetime import datetime
import google.generativeai as genai
from duckduckgo_search import DDGS # Ricerca web gratuita
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('models/gemini-flash-latest')

def cerca_news(query):
    try:
        with DDGS() as ddgs:
            # Aggiungiamo '2026' alla ricerca per forzare i risultati recenti
            risultati = ddgs.text(f"{query} gennaio 2026", max_results=3)
            testo = "\n".join([r['body'] for r in risultati])
            return testo
    except Exception as e:
        print(f"Errore ricerca: {e}")
        return ""

async def chiedi_a_gemini(prompt):
    try:
        ora = datetime.now().strftime("%H:%M")
        data = datetime.now().strftime("%d/%m/%Y")
        
        info_web = await asyncio.to_thread(cerca_news, prompt)

        istruzioni = (
            f"Oggi è il {data}, ore {ora}. Sei l'assistente di Daniele.\n"
            f"INFO WEB: {info_web}\n\n"
            "REGOLE DI RISPOSTA:\n"
            "- Rispondi in modo sintetico.\n"
            "- Usa SOLO <b>testo</b> per il grassetto.\n"
            "- NON usare mai asterischi (*) o cancelletti (#).\n"
            f"Domanda: {prompt}"
        )

        response = await asyncio.to_thread(model.generate_content, istruzioni)
        testo_finale = response.text
        
        # FIX SICUREZZA: Rimuove eventuali asterischi rimasti per errore
        testo_finale = testo_finale.replace("**", "").replace("*", "")
        
        return testo_finale
    
    except Exception as e:
        # Se l'errore è la quota (429), diamo un messaggio chiaro
        if "429" in str(e):
            return "Purtroppo ho esaurito i miei 'gettoni' giornalieri gratuiti di Gemini. 😅 Riprova tra un po' o domani!"
        print(f"DEBUG ERROR: {e}")
        return f"Errore tecnico: {e}"