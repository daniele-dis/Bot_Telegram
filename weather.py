import requests

# Dizionario per tradurre i codici Open-Meteo in testo e icone
def interpret_weather_code(code):
    weather_map = {
        0: "Cielo limpido ☀️",
        1: "Prevalentemente sereno 🌤️",
        2: "Parzialmente nuvoloso ⛅",
        3: "Nuvoloso ☁️",
        45: "Nebbia 🌫️",
        48: "Nebbia con brina 🌫️❄️",
        51: "Pioggerellina leggera 🌦️",
        53: "Pioggerellina moderata 🌦️",
        55: "Pioggerellina densa 🌦️",
        61: "Pioggia debole 🌧️",
        63: "Pioggia moderata 🌧️",
        65: "Pioggia forte 🌧️",
        71: "Neve leggera 🌨️",
        73: "Neve moderata 🌨️",
        75: "Neve forte 🌨️",
        77: "Granelli di neve ❄️",
        80: "Rovesci di pioggia deboli 🌦️",
        81: "Rovesci di pioggia moderati 🌧️",
        82: "Rovesci di pioggia violenti ⛈️",
        95: "Temporale leggero o moderato ⛈️",
        96: "Temporale con grandine leggera ⛈️🌨️",
        99: "Temporale con grandine forte ⛈️❄️",
    }
    return weather_map.get(code, "Condizioni non specificate ❓")

async def get_weather(city_name):
    try:
        city_encoded = requests.utils.quote(city_name)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_encoded}&count=1&language=it&format=json"
        geo_res = requests.get(geo_url).json()
        
        if not geo_res.get('results'):
            return f"Mi dispiace, non ho trovato '{city_name}'. Prova a scriverla diversamente."

        data = geo_res['results'][0]
        lat, lon = data['latitude'], data['longitude']
        nome_completo = f"{data['name']} ({data.get('admin1', '')}, {data.get('country', '')})"

        # Aggiungiamo 'weathercode' alla richiesta
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(weather_url).json()
        
        # Estraiamo i dati
        current = w_res['current_weather']
        temp = current['temperature']
        w_code = current['weathercode'] # Il codice numerico del meteo
        
        # Traduciamo il codice in testo leggibile
        condizione = interpret_weather_code(w_code)
        
        return (f"📍 Meteo per {nome_completo}\n\n"
                f"🌡️ Temperatura: {temp}°C\n\n"
                f"☁️ Condizione: {condizione}")

    except Exception as e:
        print(f"Errore Meteo: {e}")
        return "Errore tecnico nel recupero del meteo."