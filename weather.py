import requests

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

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(weather_url).json()
        
        temp = w_res['current_weather']['temperature']
        return f"A {nome_completo} ci sono attualmente {temp}°C. 🌡️"
    except Exception as e:
        print(f"Errore Meteo: {e}")
        return "Errore tecnico nel recupero del meteo."