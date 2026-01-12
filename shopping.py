import urllib.parse

def cerca_prezzi(prodotto):
    query = urllib.parse.quote(prodotto)
    
    # Idealo è molto più stabile per i link diretti e non dà quasi mai 404
    idealo_link = f"https://www.idealo.it/risultati.html?q={query}"
    google_link = f"https://www.google.com/search?q={query}&tbm=shop"
    ebay_link = f"https://www.ebay.it/sch/i.html?_nkw={query}&_sop=12"

    testo_risposta = (
        f"🔍 <b>Ricerca Prezzi per: {prodotto}</b>\n\n"
        f"Ho sostituito Trovaprezzi con <b>Idealo</b> perché è più affidabile e non dà errori di pagina:\n\n"
        f"📉 <a href='{idealo_link}'>Confronta su Idealo</a>\n"
        f"🛒 <a href='{google_link}'>Vedi su Google Shopping</a>\n"
        f"📦 <a href='{ebay_link}'>Vedi offerte su eBay</a>\n\n"
        f"<i>Idealo ti mostrerà subito il prezzo più basso disponibile oggi!</i>"
    )
    return testo_risposta