# NOVA: The Next-Gen Operational Virtual Assistant

Forget cookie-cutter AI tools — **NOVA** is your all-in-one digital sidekick that takes control, handles your hustle, and gets things done *your way*.

## Features

- 🎛️ **OS Control**  
  Control system-level operations like changing volume, muting, launching applications, and shutting down the system — all via natural commands.

- 📅 **Smart Scheduling**  
  Set reminders, manage to-do lists, and sync seamlessly with your Google Calendar for efficient scheduling and alerts.

- 🧠 **Image Intelligence**  
  Upload or point to images — NOVA analyzes and decodes them instantly using powerful visual AI models.

- 🔍 **Universal Smart Search**  
  Search anything from Google, YouTube, or Amazon directly via commands — no browser needed.

- 🎙️ **Multi-Mode Interaction**  
  Control NOVA using voice commands or classic text input — the choice is yours.

- 🎵 **Multimedia Control**  
  Play music, get weather updates, set moods — NOVA handles your vibes too.

- 💼 **Productivity on Autopilot**  
  Draft emails, write applications, or automate repetitive work — NOVA’s got your back.

## Tech Stack

- **Frontend**: Tkinter (Python GUI Library)
- **AI/ML Integration**: Google Gemini
- **API Integration**: Google Calendar API
- **Voice Recognition**: Python SpeechRecognition
- **OS-Level Integration**: Python (pyttsx3, pyautogui, os subprocess)
- **Storage & Sync**: LocalStorage, Session Management

## Project Structure

```bash
├── test.py             # Main file combining all the code
├── Data
│   └── chalog.json     # Contains all the previous Chatlog
├── image.py            # Image analysis AI-code
├── jarvis.py           # Contains all multi-media tasks
├── todo.py             # Contains all the calender code
├── location.py         # Utility file for calender events
├── requirements.txt    # Contains all the requirements
└── README.md
```

## Installation

> **Note**: Python Version greater than 3.8 needed.

1. **Clone the Repository**

```bash
git clone [repository-url]
cd NOVA
```

2. **Create and activate python virtual environment**

```bash
conda create -p venv python==3.12.0 -y
activate venv/
```

3. **Install all the requirements necessary for this project**

```bash
pip install -r requirements.txt
```

4. **Make an empty `Data` folder in root directory for Chatlogs and then create a file `chatlog.json` inside it**

```bash
mkdir Data
echo. > chalog.json
```

4. **Start the Python application**

```bash
python test.py
```

## Contributing

We welcome contributions from the community! Whether you're interested in improving features, fixing bugs, or adding new functionality, your input is valuable. Feel free to reach out to us with your ideas and suggestions.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
