import os
from datetime import datetime

BASE_SAVE_PATH = "foto_utenti"

def prepara_cartelle(allowed_users):
    """Crea le cartelle necessarie all'avvio."""
    if not os.path.exists(BASE_SAVE_PATH):
        os.makedirs(BASE_SAVE_PATH)
    
    for user_id in allowed_users:
        user_path = os.path.join(BASE_SAVE_PATH, str(user_id))
        if not os.path.exists(user_path):
            os.makedirs(user_path)
            print(f"Cartella creata per l'utente {user_id}")

async def salva_foto_disco(bot, user_id, file_id):
    """Scarica la foto da Telegram e la salva nella cartella utente."""
    try:
        new_file = await bot.get_file(file_id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"foto_{timestamp}.jpg"
        save_path = os.path.join(BASE_SAVE_PATH, str(user_id), file_name)
        
        await new_file.download_to_drive(save_path)
        return True, file_name
    except Exception as e:
        print(f"Errore salvataggio: {e}")
        return False, str(e)