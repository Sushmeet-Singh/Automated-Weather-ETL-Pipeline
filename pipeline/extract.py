import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = "Enter your open weather api here"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def fetch_weather(city: str) -> dict:
    params = {"q": city, "appid": API_KEY}
    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()