import requests
from typing import Tuple, Optional, Dict, Any
from backend.config import OPENWEATHER_API_KEY

def get_location_by_ip() -> Tuple[str, Optional[str], Optional[str]]:
    """
    Fetch geolocation details using the IP address from ipinfo.io.
    Returns: (location_string, latitude, longitude)
    """
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            city = data.get('city', 'Unknown City')
            region = data.get('region', 'Unknown Region')
            country = data.get('country', 'Unknown Country')
            loc = data.get('loc', '0,0')
            
            if ',' in loc:
                latitude, longitude = loc.split(',')
            else:
                latitude, longitude = None, None
                
            location = f"{city}, {region}, {country}"
            return location, latitude, longitude
    except Exception as e:
        print(f"[WeatherService] Geolocation error: {e}")
        
    return "Unable to fetch location", None, None

def get_weather(lat: Optional[str], lon: Optional[str], api_key: str = OPENWEATHER_API_KEY) -> str:
    """
    Fetch current weather description and temperature using coordinates.
    """
    if not lat or not lon:
        return "Weather unavailable (no coordinates)"
        
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            temperature = round(data['main']['temp'], 1)
            weather_desc = data['weather'][0]['description']
            return f"{temperature}°C {weather_desc.capitalize()}"
        else:
            return f"Error: {response.json().get('message', 'Unable to fetch weather')}"
    except Exception as e:
        return f"Weather unavailable ({e})"

def get_weather_details(lat: Optional[str], lon: Optional[str], api_key: str = OPENWEATHER_API_KEY) -> Dict[str, Any]:
    """
    Fetch complete weather data including location name from coordinates.
    """
    if not lat or not lon:
        loc, ip_lat, ip_lon = get_location_by_ip()
        return {
            "location": loc,
            "latitude": ip_lat,
            "longitude": ip_lon,
            "weather": get_weather(ip_lat, ip_lon, api_key)
        }

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            city = data.get('name', '')
            country = data.get('sys', {}).get('country', '')
            location_name = f"{city}, {country}" if city and country else (city or f"{lat}, {lon}")
            temperature = round(data['main']['temp'], 1)
            weather_desc = data['weather'][0]['description'].capitalize()
            return {
                "location": location_name,
                "latitude": str(lat),
                "longitude": str(lon),
                "weather": f"{temperature}°C {weather_desc}"
            }
    except Exception as e:
        print(f"[WeatherService] Coordinate weather error: {e}")

    # Fallback
    loc, ip_lat, ip_lon = get_location_by_ip()
    return {
        "location": loc,
        "latitude": ip_lat,
        "longitude": ip_lon,
        "weather": get_weather(ip_lat, ip_lon, api_key)
    }

def get_weather_by_city(city_name: str, api_key: str = OPENWEATHER_API_KEY) -> str:
    """
    Fetch current weather description and temperature using city name.
    """
    if not city_name:
        return "Please provide a city name."
    try:
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city_name.strip(), "appid": api_key, "units": "metric"}
        response = requests.get(base_url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            weather = data["weather"][0]["description"]
            temp = round(data["main"]["temp"], 1)
            return f"The current weather in {city_name} is {weather} with a temperature of {temp}°C."
        else:
            return f"Sorry, I couldn't retrieve weather for '{city_name}'."
    except Exception as e:
        return f"An error occurred while fetching weather for '{city_name}': {e}"
