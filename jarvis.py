import pyttsx3
import speech_recognition as sr
import webbrowser
import requests
import os
import sys
import random
import tkinter as tk

def main():
    def setup_jarvis():
        jarvis = pyttsx3.init()
        voices = jarvis.getProperty("voices")
        jarvis.setProperty("voice", voices[0].id)  # Select a voice
        jarvis.setProperty("rate", 200)
        return jarvis

    def wake_word_listener():
        recognizer = sr.Recognizer()
        jarvis = setup_jarvis()
        recognizer.dynamic_energy_threshold = True  # Adjust energy threshold dynamically

        jarvis.say("Hello sir. Say 'Hey JARVIS' when you need me.")
        jarvis.runAndWait()

        while True:
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    print("Listening for the wake word...")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)

                    command = recognizer.recognize_google(audio).lower()
                    print(f"You said: {command}")

                    if "hey jarvis" in command or "jarvis" in command:
                        jarvis.say("Yes, sir. How can I assist you?")
                        jarvis.runAndWait()
                        handle_command(jarvis)
            except sr.UnknownValueError:
                print("Didn't catch that. Waiting for the wake word...")
            except sr.WaitTimeoutError:
                print("No input detected. Still waiting...")
            except sr.RequestError:
                jarvis.say("There seems to be an issue with the recognition service.")
                jarvis.runAndWait()
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                jarvis.say("An error occurred. Returning to wake-word listening mode.")
                jarvis.runAndWait()

    def handle_command(jarvis):
        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True

        while True:
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    jarvis.say("Listening for your command...")
                    jarvis.runAndWait()
                
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)

                    command = recognizer.recognize_google(audio).lower()
                    print(f"You said: {command}")

                    if "weather" in command:
                        city_name = command.split("in")[-1].strip()
                        response = get_weather(city_name)
                        jarvis.say(response)
                        jarvis.runAndWait()
                    elif "search" in command:
                        query = command.replace("search for", "").strip()
                        response = google_search(query)
                        jarvis.say(response)
                        jarvis.runAndWait()
                    elif "music" in command or "songs" in command:
                        jarvis.say("Playing music now")
                        jarvis.runAndWait()
                        play(jarvis)
                    elif "sleep" in command or "that's it" in command:
                        jarvis.say("Goodnight, Sir.")
                        jarvis.runAndWait()
                        sys.exit()
                    elif "youtube" in command:
                        query = command.replace("youtube", "").strip()
                        if not query:  # If no query provided
                            jarvis.say("What should I search for?")
                            jarvis.runAndWait() 
                            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
                            query = recognizer.recognize_google(audio).lower()
                        response = youtube_search(query)
                        jarvis.say(response)
                        jarvis.runAndWait()
                    elif "whatsapp" in command:
                        os.startfile(r"C:\Users\Aditya Kurani\Desktop\WhatsApp - Shortcut.lnk")
                    else:
                        jarvis.say("Sorry, I didn't understand that command.")
                        jarvis.runAndWait()
            except sr.UnknownValueError:
                jarvis.say("I couldn't understand that. Please try again.")
                jarvis.runAndWait()
            except sr.WaitTimeoutError:
                jarvis.say("No input detected. Returning to wake-word mode.")
                jarvis.runAndWait()
                return
            except sr.RequestError:
                jarvis.say("There seems to be an issue with the recognition service.")
                jarvis.runAndWait()
                return
            except Exception as e:
                jarvis.say("An unexpected error occurred.")
                jarvis.runAndWait()
                print(f"Error: {e}")
                return

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

    def google_search(query):
        search_url = f"https://www.google.com/search?q={query}"
        webbrowser.open(search_url)
        return f"Here are the search results for {query}."

    def youtube_search(query):
        search_url = f"https://www.youtube.com/results?search_query={query}"
        webbrowser.open(search_url)
        return f"Searched YouTube for {query}"

    def play(jarvis):
        music = ["onandon.mp4", "backinblack.mp4", "millionaire.mp4", "blueeyes.mp4", "Shoot to Thrill.mp4"]
        select = random.randint(0, len(music) - 1)
        selectedmusic = music[select]
        sm = selectedmusic.split(".")[0]
        jarvis.say(f"Playing {sm}")
        jarvis.runAndWait()
        musicpath = fr"C:\Users\Aditya Kurani\Desktop\music\{selectedmusic}"
        os.startfile(musicpath)

    wake_word_listener()

main()
