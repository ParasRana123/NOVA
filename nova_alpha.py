from json import load, dump
import datetime
import requests
from groq import Groq
import  pyttsx3 
import speech_recognition as sr
# User and Assistant details
Username = "Aditya"
Assistantname = "Jarvis"
GroqAPIKey = "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"

# Initializing the Groq client
client = Groq(api_key=GroqAPIKey)

# System instructions
System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname}, which has real-time up-to-date information from the internet.
*** Provide answers in a professional way, making sure to use proper grammar, punctuation, and formal tone. ***
*** Just answer the question from the provided data in a professional way. ***"""

# Load chat history
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# Function to get current weather information
def get_weather(city_name):
    api_key = "fc3b1eb09d67c9ebd2d39e4fc7d2bb41"
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_name, "appid": api_key, "units": "metric"}
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
    non_empty_lines = [line.strip() for line  in lines if line.strip()]
    return '\n'.join(non_empty_lines)

# Main function to handle real-time responses
def RealtimeSearchEngine(prompt):
    global messages

    # Load chat history
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
    messages.append({"role": "user", "content": prompt})

    # Handle weather-related prompts
    if "weather" in prompt.lower():
        city_name = prompt.split("weather in")[-1].strip()
        weather_info = get_weather(city_name)
        system_context = {"role": "system", "content": weather_info}
    else:
        # Use date and time information for general prompts
        system_context = {"role": "system", "content": Information()}

    # Create chat completion
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "system", "content": System}, system_context] + messages,
        max_tokens=1024,
        temperature=0.7,
        top_p=1,
        stream=True
    )

    # Generate the response
    answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content

    answer = AnswerModifier(answer)
    messages.append({"role": "assistant", "content": answer})

    # Save updated chat history
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    return answer
def setup_nova():
    jarvis=pyttsx3.init()
    voices=jarvis.getProperty("voices")
    jarvis.setProperty('voice',voices[1].id)
    jarvis.setProperty('rate',240)
    return jarvis
def speak(jarvis,text):
    print(text)
    jarvis.say(text)
    jarvis.runAndWait()
stop=False
def main(user_input):
    jar = setup_nova()
    # while True:
    # user_input = input("Enter your question: ")
        
        # Exit condition
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Goodbye!")
        if not stop:
            speak(jar, "Goodbye!")
        else:jar.stop()
        
        # Process input and generate response
    response = RealtimeSearchEngine(user_input)
        
        # Provide output
    # speak(jar, response)
    return (response)
# main()