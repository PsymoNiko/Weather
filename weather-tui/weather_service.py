import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class WeatherService:
    """Handles fetching and caching weather data from OpenWeatherMap."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY not found in .env file")
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.cache = {}
        self.cache_duration = timedelta(minutes=10)  # Cache for 10 minutes

    def get_cached_weather(self, city: str):
        """Retrieves weather data from cache if it's still valid."""
        if city in self.cache:
            data, timestamp = self.cache[city]
            if datetime.now() - timestamp < self.cache_duration:
                return data
        return None

    def fetch_weather(self, city: str):
        """Fetches fresh weather data from the API for a given city."""
        cached_data = self.get_cached_weather(city)
        if cached_data:
            return cached_data

        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"  # Use metric units
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            weather_data = response.json()
            self.cache[city] = (weather_data, datetime.now())
            return weather_data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather for {city}: {e}")
            return None

    def get_temperature(self, city: str):
        """Returns the temperature in Celsius for a given city."""
        weather_data = self.fetch_weather(city)
        if weather_data:
            return weather_data['main']['temp']
        return None

    def get_full_weather(self, city: str):
        """Returns a formatted string with all relevant weather information."""
        weather_data = self.fetch_weather(city)
        if not weather_data:
            return f"Could not retrieve weather for {city}."

        temp = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        humidity = weather_data['main']['humidity']
        description = weather_data['weather'][0]['description']
        wind_speed = weather_data['wind']['speed']

        return (f"Location: {city}\n"
                f"Temperature: {temp}°C\n"
                f"Feels like: {feels_like}°C\n"
                f"Conditions: {description}\n"
                f"Humidity: {humidity}%\n"
                f"Wind Speed: {wind_speed} m/s")
