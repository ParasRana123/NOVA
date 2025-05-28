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

- **Frontend**: HTML/CSS, JavaScript (or React if used)
- **Backend**: Node.js, Express.js
- **AI/ML Integration**: Google Gemini
- **API Integration**: Google Calendar API
- **Voice Recognition**: Python SpeechRecognition
- **OS-Level Integration**: Python (pyttsx3, pyautogui, os subprocess)
- **Storage & Sync**: LocalStorage, Session Management

## Project Structure

```bash
├── static/            
│   ├── css/        # All CSS stylings in this file
│   ├── uploads/    # Contains user Uploaded images
│   └── matches/    # Matched images for the user uplaoded images
├── templates/
│   └── index.html  # Contains all the frontend HTML code
├── main.py         # Flask backend code
├── app.py          # Streamlit backend code
├── feature_extractor1.ipynb   # Useful for making filenames.pkl
├── feature_extractor.ipynb    # Useful for making embedding.pkl
├── requirements.txt           # Contains all the requirements
└── README.md
```

## Installation

> **Note**: Python Version greater than 3.7 needed.

1. **Clone the Repository**

```bash
git clone [repository-url]
cd face
```

2. **Create and activate python virtual environment**

```bash
conda create -p venv python==3.8.0 -y
activate venv/
```

3. **Install all the requirements necessary for this project**

```bash
pip install -r requirements.txt
```

4. **Install the Jupyter Notebook**

```bash
pip install notebook
```

5. **Run the `feature_extractor1.ipynb` to make `filenames.pkl`**

```bash
jupyter nbconvert --to notebook --feature.extractor1.ipynb --inplace
```

6. **Then run the `feature_extractor.ipynb` to make `embedding.pkl`**

```bash
jupyter nbconvert --to notebook --feature.extractor.ipynb --inplace
```

7. **Make the `uploads` and  `matches` inside `static` folder**

```bash
cd static
mkdir uploads
mkdir matches
```

8. **Start the flask application**

```bash
python main.py
```

   **You can also use the streamlit server (Optional)**
   ```bash
   streamlit run app.py
   ```

## Contributing

We welcome contributions from the community! Whether you're interested in improving features, fixing bugs, or adding new functionality, your input is valuable. Feel free to reach out to us with your ideas and suggestions.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
