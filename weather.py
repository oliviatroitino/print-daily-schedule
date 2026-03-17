import requests
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env from current project folder
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY") 

if not WEATHER_API_KEY:
    raise ValueError("WEATHER_API_KEY is missing in .env")

def get_weather(city: str): #https://api.openweathermap.org/data/2.5/weather?q=Madrid&appid=ff41756922e3285d644ff12e1b70eac7&units=metric
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    return {"temp": temp, "desc": desc}, None
