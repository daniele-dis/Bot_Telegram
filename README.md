# Bot_Telegram
In questo progetto, sviluppato usando Python e relative libreria, ho voluto creare un Bot Telegraam che mi aiutasse nella quotidianità con funzioni utili.
Per iniziare, son partito dalla fase di creazione dello stesso, quindi interrogando @BotFather e lanciando il comando /newbot.
A questo punto ci viene dataa la possibilità di sceglierne il nome e l'username. Fatto ciò, FatherBot ci restituirà il Token HTTP API sotto forma di stringa da utilizzare nel codice, e da includere in un file .env in modo che rimanga segreto.
D'ora in poi, inizia il vero sviluppo delle funzioni per il nostro bot.
Tra le tante funzioni disponibili, ad ora, ne sono presente diverse, che reputo utili nell'utilizzo di tutti i giorni:
-Chi sei? e Che ore sono? Restituiscono banalmente una descrizione del bot e l'orario attuale attraverso (datetime.now().strftime('%H:%M'))

-Meteo, dove dando in input al bot una città, restituisce condizioni climatiche (es: parzialmente soleggiato) e la temperatura espressa in gradi Celsius.

-Cerca Prezzi, permette di, dato un prodotto in input (es:iPhone 15), di ricevere un messaggio dal bot stesso con 3 link di riferimento, tra cui link Idealo, link Google Shopping e link Ebay che fanno riferimento direttamente al prodotto cercato, al fine di trovare il prezzo più vantaggioso.

-Spesa e Report Spese, banalmente con Spesa aggiungi le tue spese quotidiane con coppia Importo e Descrizione, che vanno a riempire file .json associati all'utente che sta utilizzando il bot al momento, e Report Spese estrae questi dati e per poter creare un report in formato .pdf in forma tabellare.

-Infine, per ora, Salva Foto, che in base a quanti utenti ALLOWED ho nel sistema, crea all'interno della cartella del progetto stesso, tante cartelle quanti sono appunto questi utenti autorizzati, e ci permette, inviata una foto al bot stesso, dal nostro rullino foto, di scegliere se salavrla o scartarla. Se decidiamo di scartarla non succede niente, se decidiamo di salvarla, la foto verrà salvata nella cartella dell'utente che al momento sta usufruendo delle funzioni del bot, alla miglior qualità possibile.

