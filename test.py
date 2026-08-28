import tkinter as tk
from tkinter import filedialog, Label, Button, Text, Scrollbar, VERTICAL, END, DISABLED, NORMAL
from threading import Thread
import time
import json
import sys
from PIL import Image, ImageSequence, ImageTk

# Import centralized services from modular backend
from backend.config import CHATLOG_PATH, OPENWEATHER_API_KEY
from backend.speech_service import speak, default_speech_service
from backend.weather_service import get_location_by_ip, get_weather
from backend.ai_service import chat as ai_chat, generate_content
from backend.vision_service import analyze_image as gemini_analyze_image
from backend.todo_service import todomain
from backend.reminder_service import reminder
from backend.os_service import (
    handle_keyboard_action,
    open_application,
    close_application,
    search_youtube,
    search_google,
    search_amazon
)
from backend.voice_listener import VoiceListener

# Initialize Root Window
root = tk.Tk()
root.title("NOVA - Virtual Assistant")
root.geometry("800x500")
root.configure(bg="#000000")

stop_flag = False
speak_enabled = True

# Voice Listener helper
def on_voice_command(command: str):
    get_response(command)

def on_voice_status(status_text: str):
    try:
        output_label.config(text=status_text)
    except Exception:
        pass

voice_listener = VoiceListener(
    on_command_callback=on_voice_command,
    on_status_update=on_voice_status
)

def get_response(user_text: str):
    """Route user query to appropriate backend services."""
    global stop_flag, speak_enabled
    if not user_text.strip():
        return

    try:
        submit_button.config(text="Processing...", state="disabled")
        cmd = user_text.lower().strip().rstrip(".,!?")
        clean_cmd = re.sub(r'^(?:hey\s+nova,?\s*|nova,?\s*|please\s+|can\s+you\s+)', '', cmd).strip()
        response = ""

        # 0. Help / Supported Commands
        if re.search(r'^(?:help|what\s+commands\s+do\s+you\s+support|what\s+can\s+you\s+do|commands\s+list|list\s+of\s+commands)$', clean_cmd):
            from backend.os_service import get_supported_commands_guide
            response = get_supported_commands_guide()

        # 1. Application Opening (e.g. "open whatsapp", "launch chrome", "open notepad")
        elif re.search(r'^(?:open|launch|start)\s+([a-zA-Z0-9\s\.\-_]+)$', clean_cmd):
            m = re.search(r'^(?:open|launch|start)\s+([a-zA-Z0-9\s\.\-_]+)$', clean_cmd)
            app_name = m.group(1).strip()
            success = open_application(app_name)
            response = f"Opening {app_name} on your device." if success else f"Attempted to open {app_name}."
            speak(response)

        # 2. Application Closing (e.g. "close whatsapp", "kill chrome")
        elif re.search(r'^(?:close|quit|kill|stop)\s+([a-zA-Z0-9\s\.\-_]+)$', clean_cmd) and "window" not in clean_cmd:
            m = re.search(r'^(?:close|quit|kill|stop)\s+([a-zA-Z0-9\s\.\-_]+)$', clean_cmd)
            app_name = m.group(1).strip()
            close_application(app_name)
            response = f"Closed application {app_name}."
            speak(response)

        # 3. YouTube Music & Playback
        elif re.search(r'^(?:play\s+(.+?)\s+on\s+youtube|play\s+(?:song|music|video)\s+(.+)|play\s+(.+))$', clean_cmd):
            m = re.search(r'^(?:play\s+(.+?)\s+on\s+youtube|play\s+(?:song|music|video)\s+(.+)|play\s+(.+))$', clean_cmd)
            query = (m.group(1) or m.group(2) or m.group(3)).strip()
            if query and query not in ["music", "song", "pause", "resume"]:
                search_youtube(query, play_first=True)
                response = f"Playing '{query}' on YouTube."
                speak(response)

        # 4. Explicit Web Searches (Google, YouTube, Amazon)
        elif re.search(r'^(?:search\s+(?:on\s+)?youtube\s+(?:for\s+)?|youtube\s+search\s+(?:for\s+)?|youtube\s+)(.+)$', clean_cmd):
            m = re.search(r'^(?:search\s+(?:on\s+)?youtube\s+(?:for\s+)?|youtube\s+search\s+(?:for\s+)?|youtube\s+)(.+)$', clean_cmd)
            query = m.group(1).strip()
            search_youtube(query)
            response = f"Searched YouTube for: {query}"
            speak(response)

        elif re.search(r'^(?:search\s+(?:on\s+)?google\s+(?:for\s+)?|google\s+search\s+(?:for\s+)?|google\s+)(.+)$', clean_cmd):
            m = re.search(r'^(?:search\s+(?:on\s+)?google\s+(?:for\s+)?|google\s+search\s+(?:for\s+)?|google\s+)(.+)$', clean_cmd)
            query = m.group(1).strip()
            search_google(query)
            response = f"Searched Google for: {query}"
            speak(response)

        elif re.search(r'^(?:search\s+(?:on\s+)?amazon\s+(?:for\s+)?|amazon\s+search\s+(?:for\s+)?|amazon\s+|buy\s+(.+?)\s+on\s+amazon)(.+)?$', clean_cmd):
            m = re.search(r'^(?:search\s+(?:on\s+)?amazon\s+(?:for\s+)?|amazon\s+search\s+(?:for\s+)?|amazon\s+|buy\s+(.+?)\s+on\s+amazon)(.+)?$', clean_cmd)
            query = (m.group(1) or m.group(2) or "").strip()
            search_amazon(query)
            response = f"Searching Amazon for: {query}"
            speak(response)

        # 5. Content Drafting (Emails, Letters, Applications, Documents)
        elif re.search(r'^(?:draft|write|compose|generate)\s+(?:an?\s+)?(?:email|letter|application|document|content)\s+(?:about|for|on)\s+(.+)$', clean_cmd) or clean_cmd.startswith("content ") or clean_cmd.startswith("email "):
            topic = re.sub(r'^(?:draft|write|compose|generate)\s+(?:an?\s+)?(?:email|letter|application|document|content)\s+(?:about|for|on)\s+|^(?:content|email)\s+', '', clean_cmd).strip()
            if topic:
                output_label.config(text=f"Generating content for: {topic}")
                response = generate_content(topic, auto_open=True)
                speak("Content generated and opened in Notepad.")

        # 6. Reminders
        elif re.search(r'^(?:remind\s+me|set\s+(?:a\s+)?reminder)\b', clean_cmd):
            success, msg = reminder(clean_cmd)
            if success:
                response = msg

        # 7. To-Do & Calendar commands
        if not response:
            todo_res = handle_todo_command(clean_cmd)
            if todo_res:
                response = todo_res

        # 8. OS Media / Keyboard macros
        if not response and re.search(r'^(?:(?:increase|decrease|raise|lower|turn\s+up|turn\s+down|mute|unmute)\s+(?:volume|sound|audio)|mute|unmute|pause|resume|next\s+track|next\s+song|previous\s+track|previous\s+song|take\s+a?\s*screenshot|screenshot|find|close\s+window)$', clean_cmd):
            handle_keyboard_action(clean_cmd)
            response = f"Executed system action: {clean_cmd}"

        # 9. Time & Date Telemetry
        elif not response and re.search(r'^(?:what\s+time\s+is\s+it|what\s+is\s+the\s+time|current\s+time|time)$', clean_cmd):
            import datetime
            now = datetime.datetime.now()
            response = f"The current time is {now.strftime('%I:%M:%S %p')} on {now.strftime('%A, %B %d, %Y')}."
            speak(response)

        # 10. Direct Weather Query
        elif not response and re.search(r'^(?:weather\s+in\s+([a-zA-Z\s]+)|what\s+is\s+the\s+weather|weather)$', clean_cmd):
            from backend.weather_service import get_weather_by_city
            m = re.search(r'^(?:weather\s+in\s+([a-zA-Z\s]+)|what\s+is\s+the\s+weather|weather)$', clean_cmd)
            city = m.group(1).strip() if m and m.group(1) else ""
            if city:
                response = get_weather_by_city(city)
            else:
                response = f"Current weather: {weather_data}"
            speak(response)

        # 11. Exit Command
        elif not response and re.search(r'^(?:goodbye|bye|sleep|exit|quit|that\'s\s+it)$', clean_cmd):
            speak("Goodbye, Sir!")
            root.destroy()
            sys.exit()

        # 12. All other queries -> Full Google Gemini conversational answer!
        if not response:
            output_label.config(text="NOVA: Thinking...")
            response = ai_chat(user_text)
            output_label.config(text=f"NOVA: {response}")
            if speak_enabled:
                speak(response)
        else:
            output_label.config(text=f"NOVA: {response}")

    except Exception as e:
        output_label.config(text=f"Error: {e}")
    finally:
        submit_button.config(text="Speak to NOVA", state="normal")

def voice_input_thread():
    """Start listening for voice input asynchronously."""
    voice_listener.start_in_background(target_method="continuous")

def stop_response():
    global speak_enabled
    speak_enabled = False
    default_speech_service.stop()
    output_label.config(text="NOVA: Speech stopped.")

def display_text():
    global speak_enabled
    speak_enabled = True

    user_text = input_box.get()
    if user_text.strip():
        input_box.delete(0, tk.END)
        Thread(target=get_response, args=(user_text,), daemon=True).start()
    else:
        output_label.config(text="NOVA: Please enter something!")

def copy_to_clipboard():
    text_to_copy = output_label.cget("text")
    root.clipboard_clear()
    root.clipboard_append(text_to_copy)
    root.update()

def display_chat():
    """Load and render chat history in GUI."""
    try:
        if CHATLOG_PATH.exists():
            with open(CHATLOG_PATH, "r", encoding="utf-8") as file:
                chat_log = json.load(file)
            chat_hist.config(state="normal")
            chat_hist.delete(1.0, tk.END)

            formatted_chat = ""
            for entry in chat_log:
                role = entry.get("role", "Unknown").capitalize()
                content = entry.get("content", "No content provided")
                formatted_chat += f"{role}: {content}\n\n"

            chat_hist.insert(tk.END, formatted_chat)
            chat_hist.config(state="disabled")
        else:
            chat_hist.config(state="normal")
            chat_hist.delete(1.0, tk.END)
            chat_hist.insert(tk.END, "No chat logs found.")
            chat_hist.config(state="disabled")
    except Exception as e:
        chat_hist.config(state="normal")
        chat_hist.delete(1.0, tk.END)
        chat_hist.insert(tk.END, f"Error loading chat log: {e}")
        chat_hist.config(state="disabled")

def upload_and_display_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")]
    )
    if file_path:
        img = Image.open(file_path)
        img = img.resize((100, 100), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_label.config(image=img_tk)
        img_label.image = img_tk
        img_label.file_path = file_path

def analyze_uploaded_image():
    if not hasattr(img_label, 'file_path') or not img_label.file_path:
        response_text.config(state=NORMAL)
        response_text.delete(1.0, END)
        response_text.insert(END, "Please upload an image first.")
        response_text.config(state=DISABLED)
        return

    def _async_analyze():
        response_text.config(state=NORMAL)
        response_text.delete(1.0, END)
        response_text.insert(END, "Analyzing image with Gemini Vision...")
        response_text.config(state=DISABLED)

        analysis = gemini_analyze_image(img_label.file_path)
        response_text.config(state=NORMAL)
        response_text.delete(1.0, END)
        response_text.insert(END, analysis)
        response_text.config(state=DISABLED)
        speak("Image analysis complete.")

    Thread(target=_async_analyze, daemon=True).start()

# Weather & Location Initialization
location, latitude, longitude = get_location_by_ip()
weather_data = get_weather(latitude, longitude, OPENWEATHER_API_KEY)

# GUI Layout & Widgets
input_box = tk.Entry(
    root, font=("Helvetica", 14), bd=0, bg="#1E1E1E", fg="#00E676",
    insertbackground="#00E676", highlightthickness=1, highlightbackground="#00E676"
)
input_box.place(x=20, y=20, width=600, height=35)
input_box.bind("<Return>", lambda event: display_text())

submit_button = tk.Button(
    root, text="Speak to NOVA", command=display_text, font=("Helvetica", 12, "bold"),
    bg="#00E676", fg="#000000", activebackground="#000000", activeforeground="#00E676",
    bd=0, relief="flat"
)
submit_button.place(x=20, y=70, width=150, height=35)

voice_button = tk.Button(
    root, text="🎤", command=voice_input_thread, font=("Helvetica", 14, "bold"),
    bg="#007BFF", fg="#FFFFFF", activebackground="#0056b3", activeforeground="#FFFFFF",
    bd=0, relief="flat"
)
voice_button.place(x=185, y=70, width=100, height=35)

copy_button = tk.Button(
    root, text="Copy", font=("Helvetica", 12), bg="#333333", fg="#FFFFFF",
    command=copy_to_clipboard, borderwidth=0, highlightthickness=0
)
copy_button.place(x=300, y=70, height=35)

output_label = tk.Label(
    root, text="NOVA is ready.", font=("Helvetica", 15), bg="#000000",
    fg="#E0E0E0", wraplength=500, justify="left"
)
output_label.place(x=10, y=120, anchor="nw")

# Siri GIF Animation
gif_path = "Sirifinal.gif"
try:
    image = Image.open(gif_path)
    gif_width = int(root.winfo_screenwidth() * 0.5)
    gif_height = int(root.winfo_screenheight() * 0.9)
    frames = [
        ImageTk.PhotoImage(frame.resize((gif_width, gif_height), Image.Resampling.LANCZOS))
        for frame in ImageSequence.Iterator(image)
    ]
except Exception as e:
    print(f"GIF Load warning: {e}")
    frames = []

gif_label = tk.Label(root, bg="#000000")
gif_label.place(relx=0.5, rely=0.6, anchor="center")

def update_gif(frame_index=0):
    if frames:
        frame = frames[frame_index]
        gif_label.config(image=frame)
        frame_index = (frame_index + 1) % len(frames)
        root.after(20, update_gif, frame_index)

if frames:
    update_gif()

# Chat History Panel
frame = tk.Frame(root, bg="#999999")
frame.place(x=1200, y=40, anchor="nw", width=700, height=350)

chat_hist = tk.Text(
    frame, font=("Helvetica", 14), bg="#000000", fg="#999999", wrap="word", height=20, width=60
)
chat_hist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame, command=chat_hist.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
chat_hist.config(yscrollcommand=scrollbar.set)

chatdisp = tk.Button(
    root, text="Previous Chat", font=("Helvetica", 17), bg="#4C4C4C", fg="#FFFFFF",
    command=display_chat, borderwidth=0, highlightthickness=0
)
chatdisp.place(x=1200, y=400, anchor="nw")

# Image Analysis Panel
img_label = Label(root, bg="#000000")
img_label.place(x=1450, y=850, height=100, width=200)

upload_button = Button(root, text="Upload Image", command=upload_and_display_image)
upload_button.place(x=1200, y=850)

analyze_button = tk.Button(root, text="Analyze Image", command=analyze_uploaded_image)
analyze_button.place(x=1320, y=850)

# Weather & Time Widgets
try:
    weather_img = Image.open("weather.jpg").resize((35, 35))
    weather_photo = ImageTk.PhotoImage(weather_img)
    weather_button = tk.Button(root, image=weather_photo, bg="black", borderwidth=0, highlightthickness=0)
    weather_button.image = weather_photo
    weather_button.place(x=820, y=235)
except Exception:
    pass

weather_info = tk.Text(
    root, fg="white", bg="black", font=("Arial", 22, "italic"), borderwidth=0, highlightthickness=0
)
weather_info.place(x=870, y=230, height=70, width=300)
weather_info.insert("1.0", weather_data)

time_label = tk.Label(root, font=("Arial", 27, "italic"), fg="white", bg="black")
time_label.place(x=870, y=300, height=70, width=200)

def update_time():
    current_time = time.strftime("%H:%M:%S")
    time_label.config(text=current_time)
    time_label.after(1000, update_time)

update_time()

# Response Text Frame
response_frame = tk.Frame(root, bg="#000000")
response_frame.place(x=1200, y=480, width=700, height=350)
response_frame.pack_propagate(False)

resp_scrollbar = Scrollbar(response_frame, orient=VERTICAL, bg="#000000")
response_text = Text(
    response_frame, wrap=tk.WORD, state=DISABLED, yscrollcommand=resp_scrollbar.set,
    bg="#000000", fg="#FFFFFF"
)
resp_scrollbar.config(command=response_text.yview)
resp_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
response_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Wake Word Activation Background Starter
def start_wake_word_listener():
    voice_listener.start_in_background(target_method="wake_word")

root.after(500, start_wake_word_listener)

if __name__ == "__main__":
    root.mainloop()