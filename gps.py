import requests
from backend.config import OPENWEATHER_API_KEY

# Function to get location by IP
def get_location_by_ip():
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        data = response.json()
        
        city = data.get('city', 'Unknown City')
        region = data.get('region', 'Unknown Region')
        country = data.get('country', 'Unknown Country')
        loc = data.get('loc', '0,0')
        
        latitude, longitude = loc.split(',') if ',' in loc else (None, None)
        location = f"{city}, {region}, {country}"
        
        return location, latitude, longitude
    except Exception as e:
        return "Unable to fetch location", None, None

# Function to get weather using latitude and longitude
def get_weather(lat, lon, api_key=OPENWEATHER_API_KEY):
    if not lat or not lon:
        return {"Error": "Coordinates missing"}
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5)
        weather_data = response.json()
        
        if response.status_code == 200:
            temperature = weather_data['main']['temp']
            weather_desc = weather_data['weather'][0]['description']
            humidity = weather_data['main']['humidity']
            wind_speed = weather_data['wind']['speed']
            
            return {
                "Temperature": f"{temperature}°C",
                "Description": weather_desc.capitalize(),
                "Humidity": f"{humidity}%",
                "Wind Speed": f"{wind_speed} m/s"
            }
        else:
            return {"Error": weather_data.get("message", "Unable to fetch weather")}
    except Exception as e:
        return {"Error": f"An error occurred while fetching weather: {e}"}

if __name__ == "__main__":
    location, latitude, longitude = get_location_by_ip()
    if latitude and longitude:
        print(f"Location: {location}")
        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")
        
        weather_info = get_weather(latitude, longitude)
        print("\nWeather Information:")
        for key, value in weather_info.items():
            print(f"{key}: {value}")
    else:
        print("Unable to fetch location or weather")