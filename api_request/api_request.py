import os
import requests
from dotenv import load_dotenv

load_dotenv()

apikey = os.getenv("WEATHER_API_KEY")
api_url = f"http://api.weatherstack.com/current?access_key={apikey}&query=Hanoi"


def get_weather_data():
    response = requests.get(api_url)
    return response.json()


if __name__ == "__main__":
    print(get_weather_data())
    
