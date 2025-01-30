import requests

# Function to get location by IP
def get_location_by_ip():
    try:
        response = requests.get("https://ipinfo.io/json")  # API for IP location
        data = response.json()
        
        # Extract location details
        city = data.get('city', 'Unknown City')
        region = data.get('region', 'Unknown Region')
        country = data.get('country', 'Unknown Country')
        loc = data.get('loc', '0,0')  # Latitude and Longitude
        
        # Split latitude and longitude
        latitude, longitude = loc.split(',')
        
        # Format location string
        location = f"{city}, {region}, {country}"
        
        # Return all details
        return location, latitude, longitude
    except Exception as e:
        return "Unable to fetch location", None, None

# Function to get weather using latitude and longitude
def get_weather(lat, lon, api_key):
    try:
        # OpenWeatherMap API URL
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        
        response = requests.get(url)
        weather_data = response.json()
        
        # Extract weather information
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
        return {"Error": "An error occurred while fetching weather"}

# Fetch location and weather
API_KEY = "fc3b1eb09d67c9ebd2d39e4fc7d2bb41"  # Replace with your OpenWeatherMap API key
location, latitude, longitude = get_location_by_ip()

if latitude and longitude:
    print(f"Location: {location}")
    print(f"Latitude: {latitude}")
    print(f"Longitude: {longitude}")
    
    # Fetch weather
    weather_info = get_weather(latitude, longitude, API_KEY)
    print("\nWeather Information:")
    for key, value in weather_info.items():
        print(f"{key}: {value}")
else:
    print("Unable to fetch location or weather")