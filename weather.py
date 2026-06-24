import requests
from datetime import datetime

class WeatherService:
    def __init__(self):
        self.geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.weather_url = "https://api.open-meteo.com/v1/forecast"

    def get_weather_data(self, city, unit="celsius"):
        try:
            # 1. Géocodage : Recherche des coordonnées GPS de la ville
            geo_params = {"name": city, "count": 1, "language": "fr"}
            geo_response = requests.get(self.geo_url, params=geo_params, timeout=5).json()
            
            if "results" not in geo_response:
                return None
            
            location_data = geo_response["results"][0]
            lat = location_data["latitude"]
            lon = location_data["longitude"]
            city_name = f"{location_data['name']}, {location_data.get('country', '')}"

            # 2. Récupération des données météo
            weather_params = {
                "latitude": lat,
                "longitude": lon,
                "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "is_day", "weather_code", "wind_speed_10m"],
                "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "precipitation_probability_max"],
                "timezone": "auto"
            }
            
            res = requests.get(self.weather_url, params=weather_params, timeout=5).json()
            current = res["current"]
            daily = res["daily"]

            # Mappage des codes météo de l'OMM
            weather_codes = {
                0: ("☀️", "Ciel dégagé"), 1: ("🌤️", "Peu nuageux"), 2: ("⛅", "Éclaircies"), 3: ("☁️", "Couvert"),
                45: ("🌫️", "Brouillard"), 48: ("🌫️", "Brouillard givrant"),
                51: ("🌧️", "Bruine légère"), 53: ("🌧️", "Bruine modérée"), 55: ("🌧️", "Bruine dense"),
                61: ("🌧️", "Pluie faible"), 63: ("🌧️", "Pluie modérée"), 65: ("🌧️", "Pluie forte"),
                71: ("❄️", "Neige faible"), 73: ("❄️", "Neige modérée"), 75: ("❄️", "Neige forte"),
                80: ("🌦️", "Averses de pluie faibles"), 81: ("🌦️", "Averses de pluie fortes"),
                95: ("⛈️", "Orage faible"), 96: ("⛈️", "Orage avec grêle")
            }

            code = current["weather_code"]
            icon, condition = weather_codes.get(code, ("✨", "Conditions variables"))

            # Prévisions sur 5 jours nettoyées de tout doublon
            forecast_list = []
            days_translation = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
            
            for i in range(1, 6):
                date_str = daily["time"][i]
                day_obj = datetime.strptime(date_str, "%Y-%m-%d")
                day_name = days_translation[day_obj.weekday()]
                
                f_code = daily["weather_code"][i]
                f_icon, _ = weather_codes.get(f_code, ("✨", "Météo"))
                
                forecast_list.append({
                    "day": "Demain" if i == 1 else day_name,
                    "icon": f_icon,
                    "max": round(daily["temperature_2m_max"][i]),
                    "min": round(daily["temperature_2m_min"][i]),
                    "rain_prob": daily["precipitation_probability_max"][i]
                })

            sunrise = daily["sunrise"][0][-5:]
            sunset = daily["sunset"][0][-5:]
            update_time = datetime.now().strftime("%H:%M:%S")

            return {
                "city": city_name,
                "temp": round(current["temperature_2m"]),
                "feels_like": round(current["apparent_temperature"]),
                "condition": condition,
                "icon": icon,
                "humidity": current["relative_humidity_2m"],
                "wind": round(current["wind_speed_10m"]),
                "sunrise": sunrise,
                "sunset": sunset,
                "is_day": current["is_day"],
                "update_time": update_time,
                "forecast": forecast_list
            }

        except Exception as e:
            print(f"Erreur technique WeatherService : {e}")
            return None