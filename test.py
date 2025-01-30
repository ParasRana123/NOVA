import tkinter as tk
from threading import Thread
from nova_alpha import main,speak,setup_nova
from PIL import Image, ImageSequence, ImageTk
import speech_recognition as sr
import json
from keyboardfunctions import handle_keyboard_action
from reminder import reminder 
from pywhatkit import playonyt
import webbrowser
from AppOpener import close , open as appopen
import requests
from PIL import Image, ImageTk
import google.generativeai as genai
from todo import todomain
import requests
import time
import pyttsx3
import subprocess
from groq import Groq

GroqAPIKey = "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"
genai.configure(api_key=("AIzaSyC_vdf5ZoD7te2A-R2tpmL0GrZgGopODfQ"))
# Initialise the groq client with the api key
client = Groq(api_key=GroqAPIKey)

from tkinter import filedialog, Label, Button, Text, Scrollbar, VERTICAL, END, DISABLED, NORMAL

speaking_flag = False  # Global flag to track speaking status
speaking_flag = False  # Global flag to track if speaking is in progress
nova=setup_nova()
def speak(nova, text):
    global speaking_flag
    speaking_flag = True  # Set flag to True when speaking starts
    print(text)
    nova.say(text)
    nova.runAndWait()  # Wait for the speech to finish
    speaking_flag = False  # Reset flag once speaking is done

root = tk.Tk()
# def openwindow():
    
root.title("nova")
root.geometry("800x500")  # Adjust window size for proportions
root.configure(bg="#000000") # Sleek dark background
stop_flag = False
speak_enabled=True
engine = pyttsx3.init()
# openwindow()


def Open(app , sess=requests.session()):
    appopen(app , match_closest=True , output=True , throw_error=True)

def closeapp(app , sess=requests.session()):
    close(app , match_closest=True,output=True,throw_error=True)

# System messages for AI chat history
messages = [{"role": "system", "content": "You are an AI assistant"}]

# Function to generate content using AI and save it to a file
def content(Topic):
    """
    Function to generate an email using AI and save it to a file.
    """

    # Nested function to open a file in Notepad
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'  # Default text editor
        subprocess.Popen([default_text_editor, File])  # Open the file in Notepad

    # Nested function to generate content using AI
    def ContentWriteAI(prompt):
        messages.append({"role": "user", "content": prompt})  # Add user's prompt to messages

        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # Specify the AI model
            messages=messages,  # Include system instructions and chat history
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""  # Initialize an empty string for the response

        # Process streaming response
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        
        Answer = Answer.replace("</sys>", "")  # Clean up any unwanted tags
        return Answer

    # Generate AI content
    ai_content = ContentWriteAI(Topic)

    # Save the content to a file
    filename = "generated_content.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(ai_content)

    # Open the file in Notepad
    OpenNotepad(filename)

def get_response(user_text):
    global stop_flag
    try:
        submit_button.config(text="Waiting...", state="disabled")
        nova = setup_nova()
        command=user_text
        found=False
        yt=False
        if "play " in command and "on youtube" in command:
            found=True
            yt=True
            query = command.replace("play ", "").replace(" on youtube", "").strip()
            playonyt(query)
        keyboardlist = [
                    "increase","decrease", "mute", "unmute", "play", "pause","next track", "previous track", "type", "find",
                    "screenshot" , "email" , "content"
                ]
        for char in keyboardlist:
            if char in command:
                found=True
                handle_keyboard_action(char)
        if "reminder" in command or "remind" in command:
            found=True
            # print("reminder is wokring")
            reminder(command)
        elif "close" in command:
            found=True
            app=command.replace("close","").strip()
            closeapp(app)
        elif "youtube" in command and not yt:
            query = command.replace("youtube", "").strip()
            search_url = f"https://www.youtube.com/results?search_query={query}"
            webbrowser.open(search_url)
            speak(f"Searched for{query}")
        elif "google" in command:
            query = command.replace("google", "").strip()
            search_url = f"https://www.google.com/search?q={query}"
            webbrowser.open(search_url)
            found=True

        elif "email" in command or "content" in command:
            found = True
            query = command
            # query = command.replace("content", "").strip()
            if query:
                content(query)
                output_label.config(text=f"Generating content for: {query}")
            else:
                output_label.config(text="Please provide a topic after 'content'.")

        elif "list" in command or "calendar" in command or "tasks" in command or "remove" in command :
            found=True
            todomain(command)
        elif "open" in command:
            found=True
            app=command.replace("open","").strip()
            Open(app)
        elif "amazon" in command:
            found=True
            # query = command.replace("search on amazon ", "").strip()
            query = ""
            querybool = False

            for char in command:
                if querybool:
                    query += char  # Start capturing the query after "for"
                elif query.endswith("for"):
                    querybool = True
                    query = ""  # Reset query after detecting "for"
                else:
                    query += char

            # print(query.strip()) 
            search_url = f"https://www.amazon.com/s?k={query}"
            webbrowser.open(search_url)
        elif "bye" in command or "sleep" in command:
            found=True
            import sys
            speak(nova,"Goodbye")
            root.destroy()
            sys.exit()
        if not found:    
            print("this is the general")
            response = main(user_text)

            retry_count = 0
            max_retries = 10
            while not response and retry_count < max_retries:
                if stop_flag:  # Check if stop flag is set
                    output_label.config(text="nova: Stopped.")
                    return  # Exit the function
                retry_count += 1
            
            if not response:
                output_label.config(text="nova: No response received. Please try again.")
            else:
                output_label.config(text=f"nova: {response}")
                if speak_enabled:
                    speak(nova, response)
    except Exception as e:
        output_label.config(text=f"Error: {e}")
    finally:
        submit_button.config(text="Speak to nova", state="normal")

import speech_recognition as sr
from threading import Thread

def voice_input():
    """Continuously listen for voice commands until stop_flag is set."""
    global stop_flag, speaking_flag
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True  # Adjust energy threshold dynamically

    while not stop_flag:  # Listen until the stop flag is True
        if speaking_flag:  # If Nova is speaking, stop listening and do not update text
            continue  # Skip listening until speaking finishes

        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Adjust for background noise
                output_label.config(text="nova: Listening for your command...")

                # Listen for a command
                audio = recognizer.listen(source, timeout=0, phrase_time_limit=5)
                
                if stop_flag:  # Break the loop if the stop flag is set
                    output_label.config(text="nova: Listening stopped.")
                    break
                
                command = recognizer.recognize_google(audio).lower()
                output_label.config(text=f"Recognized: {command}")

                # Call the get_response function in a separate thread
                thread = Thread(target=get_response, args=(command,))
                thread.start()

        except sr.UnknownValueError:
            if not speaking_flag:  # Only show the error if Nova isn't speaking
                output_label.config(text="nova: I couldn't understand that. Please try again.")
        except sr.WaitTimeoutError:
            if not speaking_flag:  # Only show the error if Nova isn't speaking
                output_label.config(text="nova: No input detected. Please try again.")
        except sr.RequestError:
            if not speaking_flag:  # Only show the error if Nova isn't speaking
                output_label.config(text="nova: Issue with the recognition service.")
        except Exception as e:
            if not speaking_flag:  # Only show the error if Nova isn't speaking
                output_label.config(text=f"nova: An unexpected error occurred: {e}")



def stop_response():
    global speak_enabled
    speak_enabled = False
    engine.stop()
    output_label.config(text="nova: Speech stopped.")  # Update UI
    toggle_speech()

def toggle_speech():
    global speak_enabled
    if speak_enabled:
        stop_response()
    else:
        speak_enabled = True
        print("Speech Enabled.")

def voice_input_thread():
    global stop_flag
    stop_flag = False 
    thread = Thread(target=voice_input)
    thread.start()


def voice_input_thread():
    """Run the voice input function in a separate thread to avoid freezing the UI."""
    thread = Thread(target=voice_input)
    thread.start()




# Function to speak the text
def speak_text(text):
    global speak_enabled
    if speak_enabled:
        engine.say(text)
        engine.runAndWait()

def display_text():
    global speak_enabled
    speak_enabled = True

    user_text = input_box.get()
    if user_text.strip():
        input_box.delete(0, tk.END)  # Clear the input box

        # Add user text to the response frame
        response_text.config(state=tk.NORMAL)
        response_text.config(state=tk.DISABLED)

        # Start a new thread to handle the AI response
        thread = Thread(target=get_response, args=(user_text,))
        thread.start()
    else:
        # Show a message in the response frame if the input is empty
        response_text.config(state=tk.NORMAL)
        response_text.insert(tk.END, "nova: Please enter something!\n")
        response_text.config(state=tk.DISABLED)

response_text = tk.Text(
    # response_frame,
    wrap=tk.WORD,  # Enable word wrapping
    bg="#000000",  # Background color
    fg="#FFFFFF",  # Text color
    font=("Helvetica", 12),  # Font style and size
    # yscrollcommand=scrollbar.set,  # Link scrollbar to text widget
    state=tk.DISABLED,  # Disable direct editing
)

response_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
submit_button = tk.Button(
    root,
    text="Speak to nova",
    command=display_text,  # This should be your function to update response_text
    font=("Helvetica", 12, "bold"),
    bg="#00E676",  # Button background color
    fg="#000000",  # Button text color
    activebackground="#000000",  # Background color when the button is active
    activeforeground="#00E676",  # Text color when the button is active
    bd=0,  # No border
    relief="flat",  # Flat button style
)#tion the button
submit_button.place(x=20, y=70, width=150, height=35)
def update_gif(frame_index=0):
    global frames
    frame = frames[frame_index]
    gif_label.config(image=frame)
    frame_index = (frame_index + 1) % len(frames)
    root.after(10, update_gif, frame_index)
def display_chat():
    try:
        with open('Data/ChatLog.json', "r") as file:
            chat_log = json.load(file)
            chat_hist.config(state="normal")  # Allow editing to update content
            chat_hist.delete(1.0, tk.END)  # Clear the existing text

            formatted_chat = ""
            for entry in chat_log:
                role = entry.get("role", "Unknown").capitalize()
                content = entry.get("content", "No content provided")
                formatted_chat += f"{role}: {content}\n"

            chat_hist.insert(tk.END, formatted_chat)
            chat_hist.config(state="disabled")  # Disable editing after updating
    except FileNotFoundError:
        chat_hist.config(state="normal")
        chat_hist.delete(1.0, tk.END)
        chat_hist.insert(tk.END, "Error: Chat log file not found.")
        chat_hist.config(state="disabled")
    except json.JSONDecodeError:
        chat_hist.config(state="normal")
        chat_hist.delete(1.0, tk.END)
        chat_hist.insert(tk.END, "Error: Chat log file is not a valid JSON.")
        chat_hist.config(state="disabled")

def upload_and_display_image():
    # Open a file dialog to select an image file
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", ".jpg;.jpeg;*.png")]
    )
    if file_path:
        # Open and display the image
        img = Image.open(file_path)
        img = img.resize((100, 100), Image.Resampling.LANCZOS)
        # img.thumbnail((100, 100))  # Resize for display purposes
        img_tk = ImageTk.PhotoImage(img)
        img_label.config(image=img_tk)
        img_label.image = img_tk
        img_label.file_path = file_path  # Store file path for analysis

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
    
location, latitude, longitude = get_location_by_ip()
API_KEY = "fc3b1eb09d67c9ebd2d39e4fc7d2bb41"
# n to get weather using latitude and longitude
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
            
            return f"{temperature}°C {weather_desc.capitalize()}"
        else:
            return f"Error: {weather_data.get('message', 'Unable to fetch weather')}"
    except Exception as e:
        return "An error occurred while fetching weather"

weather_data = get_weather(latitude, longitude, API_KEY)
# Function to get and update the current time
def update_time():
    # Get the current time in HH:MM:SS format
    current_time = time.strftime("%H:%M:%S")
    # Update the time label with the current time
    time_label.config(text=current_time)
    # Call the update_time function after 1000 ms (1 second)
    time_label.after(1000, update_time)
gif_path = "Sirifinal.gif"  # Replace with the path to your GIF
image = Image.open(gif_path)

gif_width = int(root.winfo_screenwidth() * 0.5)
gif_height = int(root.winfo_screenheight() * 0.9)
frames = [
    ImageTk.PhotoImage(frame.resize((gif_width, gif_height), Image.Resampling.LANCZOS))
    for frame in ImageSequence.Iterator(image)
]

gif_label = tk.Label(root, bg="#000000")
gif_label.place(relx=0.5, rely=0.6, anchor="center")  # Positioned at 70% width and center height
update_gif()
voice_button = tk.Button(
    root,
    text="🎤", 
    command=voice_input_thread, 
    font=("Helvetica", 14, "bold"),
    bg="#007BFF",
    fg="#FFFFFF",
    activebackground="#0056b3",
    activeforeground="#FFFFFF",
    bd=0,
    relief="flat"
)
button_size = 50  # Button size (width and height)
voice_button.place(
    x=200, y=70, width=100, height=35
)
voice_button.config(borderwidth=0, highlightthickness=0)
voice_button.place(x=185,y=70,width=100,height=35)
input_box = tk.Entry(
    root,
    font=("Helvetica", 14),
    bd=0,
    bg="#1E1E1E",
    fg="#00E676",
    insertbackground="#00E676",  # Cursor color
    highlightthickness=1,
    highlightbackground="#00E676"
)
input_box.place(x=20, y=20, width=600, height=35)  # Top-left corner
def copy_to_clipboard():
    text_to_copy = output_label.cget("text") 
    root.clipboard_clear()  # Clear the clipboard
    root.clipboard_append(output_label['text'])  # Copy the label's text
    root.update()  # Ensure the clipboard gets updated
output_label = tk.Label(
    root,
    text="",
    font=("Helvetica", 17),
    bg="#000000",  # Pure black background
    fg="#E0E0E0",  # Light gray text
    wraplength=500,
    justify="left"
)
output_label.place(x=10, y=120, anchor="nw")  # Positioned in the top-left corner

copy_button = tk.Button(
    root,
    text="Copy",
    font=("Helvetica", 12),
    bg="#333333",  # Dark gray background
    fg="#FFFFFF",  # White text
    command=copy_to_clipboard,
    borderwidth=0 , 
    highlightthickness=0
)
copy_button.place(x=300, y=70, anchor="nw" , height=35)

frame = tk.Frame(root, bg="#999999")
frame.place(x=1200, y=40, anchor="nw" , width=700 , height=350)
chat_hist = tk.Text(
    frame,
    font=("Helvetica", 14),
    bg="#000000",
    fg="#999999",
    wrap="word",
    height=20,
    width=60
)
chat_hist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
# chat_hist.place(x=1200,y=400,anchor="n")
scrollbar = tk.Scrollbar(frame, command=chat_hist.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

chat_hist.config(yscrollcommand=scrollbar.set)
chatdisp = tk.Button(
    root,
    text="Previous Chat",
    font=("Helvetica", 17),
    bg="#4C4C4C",
    fg="#FFFFFF",
    command=display_chat,
    borderwidth=0 , 
    highlightthickness=0
)
chatdisp.place(x=1200, y=400, anchor="nw")  # Adjust position as needed
# thsi si the image funcitons
import tkinter as tk
from tkinter import Scrollbar, Text, Label, Button, VERTICAL, DISABLED

nova=setup_nova()
img_label = Label(root , bg="#000000")
img_label.place(x=1450 , y = 850 , height=100 , width=200)

upload_button = Button(root, text="Upload Image", command=upload_and_display_image)
upload_button.place(x=1200, y=850)

analyze_button = tk.Button(
    root, text="Analyze Image", 
    command=lambda: analyze_image(nova)
    )
analyze_button.place(x=1320 , y = 850)

image = Image.open("weather.jpg")  # Replace with your image file path
image = image.resize((35, 35))  # Resize the image to fit the button
photo = ImageTk.PhotoImage(image)
weather_button = tk.Button(
    root, image=photo, bg="black" , borderwidth=0 , highlightthickness=0
    )
weather_button.place(x=820 , y =235)

weather_info = tk.Text(
    root, fg="white" , bg="black", font=("Arial", 22, "italic") ,  borderwidth=0 , highlightthickness=0
    )
weather_info.place(x=870 , y = 230 , height=70 , width=300)
weather_info.insert("1.0", weather_data)
time_label = tk.Label(root, font=("LED Board", 27, "italic"), fg="white", bg="black")
time_label.place(x=870 , y = 300 , height=70 , width=200)
update_time()
response_frame = tk.Frame(root, bg="#000000")
response_frame.place(x=1200, y=480, width=700, height=350)
response_frame.pack_propagate(False)
scrollbar = Scrollbar(response_frame, orient=VERTICAL , bg="#000000")
response_text = Text(
    response_frame, 
    wrap=tk.WORD, 
    width=6, 
    height=4, 
    state=DISABLED, 
    yscrollcommand=scrollbar.set,
    bg="#000000",  # Set background to black
    fg="#FFFFFF"   # Set text color to white for better visibility
)
scrollbar.config(command=response_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
response_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

def voiceactivation():
    recognizer = sr.Recognizer()
    nova = setup_nova()
    recognizer.dynamic_energy_threshold = True  # Adjust energy threshold dynamically
    nova.say("Hello sir. Say 'Hey Nova' when you need me.")
    nova.runAndWait()        
    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                output_label.config(text="Listening for the wake word...")
                audio = recognizer.listen(source, timeout=0, phrase_time_limit=5)
                command = recognizer.recognize_google(audio).lower()
                # print(f"You said: {command}")

                if "hey nova" in command or "nova" in command:
                        nova.say("Yes, sir. How can I assist you?")
                        nova.runAndWait()
                        voice_input()
                        break
        except sr.UnknownValueError:
                print("Didn't catch that. Waiting for the wake word...")
        except sr.WaitTimeoutError:
                print("No input detected. Still waiting...")
        except sr.RequestError:
                nova.say("There seems to be an issue with the recognition service.")
                nova.runAndWait()
        except Exception as e:
                print(f"An unexpected error occurred: {e}")
                nova.say("An error occurred. Returning to wake-word listening mode.")
                nova.runAndWait() 
def analyze_image(nova):
    try:
        file_path = img_label.file_path
        with open(file_path, "rb") as image_file:
            image_data = image_file.read()


        image_parts = [
            {
                "mime_type": "image/jpeg",  # Adjust based on your image type
                "data": image_data
            }
        ]

        input_prompt = """
        You are an Image Analyzer with expertise in identifying and understanding the contents of any given image. Users can upload any type of image, and your role is to provide a detailed analysis of what is present in the image along with meaningful insights.

        For each image, provide:
        1. A description of the key objects, people, or elements in the image and make the response small.
        2. Insights or potential applications related to the image (e.g., identifying objects for e-commerce, detecting scenarios for industrial use, or analyzing visuals for creative projects).
        3. Suggestions for enhancing or utilizing the image further (e.g., improvements for clarity, creative edits, or technological applications).
        
        Please ensure the insights are clear, actionable, and tailored to the context of the uploaded image.
        
        """

        model = genai.GenerativeModel('gemini-1.5-pro')
        response = (model.generate_content([input_prompt, image_parts[0]]))
        nova.say(response)
        response_text.insert(END , nova)
        response_text.config(state=NORMAL)
        response_text.delete(1.0, END)
        response_text.insert(END, response.text)
        response_text.config(state=DISABLED)

    except AttributeError:
        response_text.config(state=NORMAL)
        response_text.delete(1.0, END)
        response_text.insert(END, "Please upload an image first.")
        response_text.config(state=DISABLED)
    except Exception as e:
        response_text.config(state=NORMAL)
        response_text.delete(1.0, END)
        response_text.insert(END, f"An error occurred: {e}")
        response_text.config(state=DISABLED)

def voice_activation_thread():  # Runs in a separate thread
    voiceactivation()
import threading
def start_voice_activation():  # Called by root.after()
    activation_thread = threading.Thread(target=voice_activation_thread)
    activation_thread.daemon = True
    activation_thread.start()


root.after(500, start_voice_activation) # Delay to allow full initialization

root.mainloop()