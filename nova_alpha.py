from json import load, dump
import datetime
import requests
import pyttsx3
import speech_recognition as sr
from backend.config import GEMINI_API_KEY, GEMINI_MODEL, OPENWEATHER_API_KEY, USER_NAME, ASSISTANT_NAME

try:
    import google.generativeai as genai
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel(GEMINI_MODEL)
    else:
        gemini_model = None
except ImportError:
    genai = None
    gemini_model = None

# User and Assistant details
Username = USER_NAME
Assistantname = ASSISTANT_NAME

# Load chat history
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# Function to get current weather information
def get_weather(city_name):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_name, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"The current weather in {city_name} is {weather} with a temperature of {temp}°C."
    else:
        return "Sorry, I couldn't retrieve the weather information."

# Function to get current date and time information
def Information():
    current_date_time = datetime.datetime.now()
    info = (
        f"Use this real-time information if needed:\n"
        f"Day: {current_date_time.strftime('%A')}\n"
        f"Date: {current_date_time.strftime('%d')}\n"
        f"Month: {current_date_time.strftime('%B')}\n"
        f"Year: {current_date_time.strftime('%Y')}\n"
        f"Time: {current_date_time.strftime('%H:%M:%S')}\n"
    )
    return info

# Function to clean up the chatbot's response
def AnswerModifier(answer):
    lines = answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

# Main function to handle real-time responses
def RealtimeSearchEngine(prompt):
    global messages
    if not gemini_model:
        return "Gemini AI model is not configured."

    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
    messages.append({"role": "user", "content": prompt})

    if "weather" in prompt.lower():
        city_name = prompt.split("weather in")[-1].strip()
        weather_info = get_weather(city_name)
        system_context = f"Weather info: {weather_info}"
    else:
        system_context = Information()

    full_prompt = f"{system_context}\n\nUser Question: {prompt}"
    try:
        response = gemini_model.generate_content(full_prompt)
        answer = response.text if response and hasattr(response, 'text') else ""
        answer = AnswerModifier(answer)
        messages.append({"role": "assistant", "content": answer})

        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return answer
    except Exception as e:
        return f"Gemini error: {e}"

def setup_nova():
    jarvis = pyttsx3.init()
    voices = jarvis.getProperty("voices")
    if len(voices) > 1:
        jarvis.setProperty('voice', voices[1].id)
    jarvis.setProperty('rate', 240)
    return jarvis

def speak(jarvis, text):
    print(text)
    jarvis.say(text)
    jarvis.runAndWait()

stop = False
def main(user_input):
    jar = setup_nova()
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Goodbye!")
        if not stop:
            speak(jar, "Goodbye!")
        else:
            jar.stop()
        return "Goodbye!"
        
    response = RealtimeSearchEngine(user_input)
    return response