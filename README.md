# NOVA: The Next-Gen Operational Virtual Assistant

Forget cookie-cutter AI tools — **NOVA** is your all-in-one digital sidekick that takes control, handles your hustle, and gets things done *your way*.

---

### 🌐 Live Links

- **Live Website**: [https://nova-inky-iota.vercel.app/](https://nova-inky-iota.vercel.app/)
- **Live Demo Video**: [Watch Demo](https://res.cloudinary.com/d3ukbssg/video/upload/v1787560321/nova_record.mp4)

---

## 🚀 Features

- 🎛️ **OS Control**: System-level operations like volume adjustments, muting, application launching (WhatsApp, Paytm, LinkedIn, Spotify, YouTube, VS Code, Settings), and playback controls.
- 📅 **Smart Scheduling**: Set reminders, manage to-do lists, priority categorizations, and sync with Google Calendar.
- 🧠 **Image Intelligence**: Upload images — NOVA analyzes and extracts insights using Google Gemini Vision.
- 🔍 **Universal Smart Search**: Search Google, YouTube, or Amazon directly via natural commands.
- 🎙️ **Multi-Mode Interaction**: Control NOVA using real-time streaming voice commands (Web Speech API / SpeechRecognition) or text input.
- 🎵 **Multimedia & Telemetry**: Play music on YouTube, get real-time GPS weather updates, and digital LED time display.
- 💼 **Productivity on Autopilot**: Draft emails, applications, or documents using Google Gemini fast models.

## 🛠️ Tech Stack

- **Frontend**: React (Vite, Vanilla CSS, Cyber & Glassmorphism Design System)
- **Backend**: Python (Modular architecture with Google Gemini, Flask REST API & Tkinter GUI)
- **API Integration**: Google Gemini API, Google Calendar API v3, OpenWeatherMap API, ipinfo.io
- **Deployment**: Vercel (Frontend SPA) & Render (Backend Web Service with Gunicorn)

## 📁 Project Structure

```bash
NOVA/
├── backend/                # Modular Python backend package
│   ├── server.py           # Flask REST API server (Gunicorn entrypoint)
│   ├── test.py             # Tkinter Desktop GUI
│   ├── requirements.txt    # Production Python dependencies
│   ├── ai_service.py       # Google Gemini LLM & content drafting
│   ├── vision_service.py   # Gemini Vision analyzer
│   ├── speech_service.py   # pyttsx3 speech synthesizer & markdown cleaner
│   ├── calendar_service.py # Google Calendar integration
│   ├── todo_service.py     # Task list & priority sorting
│   ├── reminder_service.py # Natural language reminders & timers
│   ├── os_service.py       # Keyboard actions & app management
│   ├── weather_service.py  # Geolocation & weather telemetry
│   ├── voice_listener.py   # Speech recognition loop
│   └── config.py           # Centralized configuration & environment loader
├── frontend/               # React Web Application (Vite)
│   ├── src/
│   │   ├── components/     # CommandBar, SiriVisualizer, WeatherClock, VisionAnalyzer, FormattedMarkdown, etc.
│   │   ├── services/api.js # Dynamic API bridge client (supports VITE_API_URL & GPS)
│   │   ├── App.jsx         # Main cyber dashboard layout
│   │   ├── App.css         # Component styling & typography
│   │   └── index.css       # Global design tokens & futuristic styling
│   ├── public/             # Visual assets (Sirifinal.gif, weather.jpg, icons)
│   ├── vercel.json         # Vercel SPA routing configuration
│   └── .env.example        # Frontend environment template
├── render.yaml             # Render deployment blueprint
├── vercel.json             # Root Vercel deployment configuration
├── Data/                   # Persistent chat history
├── Tasks/                  # Priority task files
└── .env.example            # Backend environment template
```

---

## 🌐 Production Deployment Guide

### Part 1: Deploying the Backend on Render (Web Service)

1. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** ➔ **Web Service**.
2. Connect your GitHub repository (`ParasRana123/NOVA`).
3. Configure the Web Service settings:
   - **Name**: `nova-backend` (or your preferred name)
   - **Language**: `Python 3`
   - **Region**: `Oregon (US West)` (or closest region)
   - **Branch**: `main`
   - **Root Directory**: *(Leave empty)*
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `gunicorn --chdir backend server:app --bind 0.0.0.0:$PORT`
4. Add the following **Environment Variables** in the Render settings:
   - `GEMINI_API_KEY`: `your_gemini_api_key`
   - `OPENWEATHER_API_KEY`: `your_openweather_api_key`
   - `USER_NAME`: `Paras`
   - `ASSISTANT_NAME`: `NOVA`
   - `PYTHON_VERSION`: `3.11.9`
5. Click **Create Web Service**.
6. Once deployed, copy your Render URL (e.g. `https://nova-backend.onrender.com`).

---

### Part 2: Deploying the Frontend on Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New...** ➔ **Project**.
2. Select your GitHub repository (`ParasRana123/NOVA`).
3. In **Project Settings**:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click *Edit* and select **`frontend`**
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Expand **Environment Variables** and add:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://your-backend-app.onrender.com` *(Paste your Render backend URL)*
5. Click **Deploy**.

---

## 💻 Local Development Guide

### 1. Backend Server
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Setup .env
cp .env.example .env

# Run API server
python backend/server.py
```
*API runs at `http://127.0.0.1:5000`*

### 2. Frontend Development Server
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs at `http://localhost:5173`*

### 3. Tkinter Desktop GUI (Optional)
```bash
python backend/test.py
```

## 📜 License
This project is licensed under the MIT License.