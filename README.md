# NOVA: The Next-Gen Operational Virtual Assistant

Forget cookie-cutter AI tools — **NOVA** is your all-in-one digital sidekick that takes control, handles your hustle, and gets things done *your way*.

## 🚀 Features

- 🎛️ **OS Control**: Control system-level operations like changing volume, muting, launching applications, and controlling playback.
- 📅 **Smart Scheduling**: Set reminders, manage to-do lists, and sync with your Google Calendar for alerts.
- 🧠 **Image Intelligence**: Upload images — NOVA analyzes and extracts insights using Google Gemini Vision.
- 🔍 **Universal Smart Search**: Search Google, YouTube, or Amazon directly via commands.
- 🎙️ **Multi-Mode Interaction**: Control NOVA using voice commands (Web Speech API / SpeechRecognition) or text input.
- 🎵 **Multimedia & Telemetry**: Play music on YouTube, get real-time weather updates, and digital LED time display.
- 💼 **Productivity on Autopilot**: Draft emails, applications, or documents using Groq Mixtral models.

## 🛠️ Tech Stack

- **Frontend**: React (Vite, Vanilla CSS, Cyber & Glassmorphism Design System) & Tkinter Desktop GUI
- **Backend**: Python (Modular architecture with Groq LLaMA-3, Google Gemini, Flask REST API)
- **API Integration**: Google Calendar API v3, OpenWeatherMap API, ipinfo.io
- **Voice Recognition**: Web Speech API & Python SpeechRecognition
- **Speech Synthesis**: Browser Web Speech Synthesis & Python pyttsx3
- **OS-Level Integration**: Python (`pyautogui`, `keyboard`, `AppOpener`, `subprocess`)

## 📁 Project Structure

```bash
NOVA/
├── backend/                # Modular Python backend package
│   ├── ai_service.py       # Groq LLM & content generation
│   ├── vision_service.py   # Gemini Vision analyzer
│   ├── speech_service.py   # pyttsx3 speech synthesizer
│   ├── calendar_service.py # Google Calendar integration
│   ├── todo_service.py     # Task list & priority sorting
│   ├── reminder_service.py # Natural language reminders & timers
│   ├── os_service.py       # Keyboard actions & app management
│   ├── weather_service.py  # Geolocation & weather telemetry
│   ├── voice_listener.py   # Speech recognition loop
│   └── config.py           # Centralized configuration & environment loader
├── frontend/               # React Web Application (Vite)
│   ├── src/
│   │   ├── components/     # CommandBar, SiriVisualizer, WeatherClock, VisionAnalyzer, etc.
│   │   ├── services/api.js # API bridge client
│   │   ├── App.jsx         # Main cyber dashboard layout
│   │   └── index.css       # Global design tokens & futuristic styling
│   └── public/             # Visual assets (Sirifinal.gif, weather.jpg)
├── server.py               # Flask REST API server bridging React to backend
├── test.py                 # Tkinter Desktop GUI
├── Data/
│   └── chatlog.json        # Persistent chat history
├── Tasks/                  # Priority task files
├── .env.example            # Environment variables template
└── requirements.txt        # Python dependencies
```

## 💻 Quickstart Guide

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/ParasRana123/NOVA.git
cd NOVA

# Install Python requirements
pip install -r requirements.txt

# Configure your API keys in .env
cp .env.example .env
```

### 2. Start the Backend API Server
```bash
python server.py
```
*API runs at `http://127.0.0.1:5000`*

### 3. Start the React Frontend
```bash
cd frontend
npm install
npm run dev
```
*Web dashboard opens at `http://localhost:5173`*

### 4. Running the Original Tkinter Desktop App (Optional)
```bash
python test.py
```

## 📜 License
This project is licensed under the MIT License.
