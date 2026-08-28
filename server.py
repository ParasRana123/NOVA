import os
import json
import base64
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import NOVA backend services
from backend.config import CHATLOG_PATH, OPENWEATHER_API_KEY, BASE_DIR
from backend.speech_service import speak, default_speech_service
from backend.weather_service import get_location_by_ip, get_weather
from backend.ai_service import chat as ai_chat, generate_content
from backend.vision_service import analyze_image as gemini_analyze_image
from backend.todo_service import handle_todo_command
from backend.reminder_service import reminder
from backend.os_service import (
    handle_keyboard_action,
    open_application,
    close_application,
    search_youtube,
    search_google,
    search_amazon
)

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for React frontend

UPLOAD_FOLDER = BASE_DIR / "Data" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "assistant": "NOVA",
        "version": "2.0.0"
    })

@app.route('/api/weather', methods=['GET'])
def get_weather_telemetry():
    """Fetch current location and weather details."""
    try:
        location, lat, lon = get_location_by_ip()
        weather_desc = get_weather(lat, lon, OPENWEATHER_API_KEY)
        return jsonify({
            "location": location,
            "latitude": lat,
            "longitude": lon,
            "weather": weather_desc
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat-history', methods=['GET'])
def get_chat_history():
    """Return stored chat history from chatlog.json."""
    try:
        if CHATLOG_PATH.exists():
            with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
                history = json.load(f)
            return jsonify({"history": history})
        return jsonify({"history": []})
    except Exception as e:
        return jsonify({"error": str(e), "history": []}), 500

@app.route('/api/chat', methods=['POST'])
def process_chat():
    """Process voice or text prompt through NOVA's command router and LLM."""
    data = request.get_json() or {}
    user_text = data.get("query", "").strip()
    voice_enabled = data.get("speak", True)

    if not user_text:
        return jsonify({"error": "Empty query"}), 400

    command = user_text.lower()
    command_type = "general_chat"
    response_text = ""

    try:
        # YouTube playback
        if "play " in command and "on youtube" in command:
            command_type = "multimedia"
            query = command.replace("play ", "").replace(" on youtube", "").strip()
            search_youtube(query, play_first=True)
            response_text = f"Playing {query} on YouTube."

        # Keyboard & OS Media Control
        elif any(k in command for k in ["increase", "decrease", "mute", "unmute", "pause", "next track", "previous track", "screenshot"]):
            command_type = "os_control"
            for k in ["increase", "decrease", "mute", "unmute", "pause", "next track", "previous track", "screenshot"]:
                if k in command:
                    handle_keyboard_action(k)
                    response_text = f"Executed system command: {k}"
                    break

        # Reminders
        elif "reminder" in command or "remind" in command:
            command_type = "reminder"
            success = reminder(command)
            response_text = f"Processed reminder: {user_text}" if success else "Failed to parse reminder time."

        # App Closing
        elif "close" in command and "close window" not in command:
            command_type = "app_management"
            app_name = command.replace("close", "").strip()
            close_application(app_name)
            response_text = f"Closed application: {app_name}"

        # Web Searches
        elif "youtube" in command:
            command_type = "search"
            query = command.replace("youtube", "").strip()
            search_youtube(query)
            response_text = f"Searched YouTube for: {query}"

        elif "google" in command:
            command_type = "search"
            query = command.replace("google", "").strip()
            search_google(query)
            response_text = f"Searched Google for: {query}"

        elif "amazon" in command:
            command_type = "search"
            query = command.split("amazon")[-1].replace("for", "").strip()
            search_amazon(query)
            response_text = f"Searched Amazon for: {query}"

        # Content Generation
        elif "email" in command or "content" in command:
            command_type = "content_drafting"
            query = command.replace("email", "").replace("content", "").strip()
            if query:
                response_text = generate_content(query, auto_open=True)
            else:
                response_text = "Please specify what content you would like me to draft."

        # To-Do & Calendar
        elif any(k in command for k in ["list", "calendar", "tasks", "remove task", "add in my list"]):
            command_type = "todo_calendar"
            handle_todo_command(command)
            response_text = f"Processed task/calendar command: {user_text}"

        # App Opening
        elif "open" in command:
            command_type = "app_management"
            app_name = command.replace("open", "").strip()
            open_application(app_name)
            response_text = f"Opening {app_name}"

        # General LLM Chat Fallback
        else:
            command_type = "ai_chat"
            response_text = ai_chat(user_text)

        # Voice output
        if voice_enabled and response_text and command_type == "ai_chat":
            default_speech_service.speak(response_text, block=False)

        return jsonify({
            "query": user_text,
            "response": response_text,
            "command_type": command_type,
            "status": "success"
        })

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image_endpoint():
    """Analyze uploaded image using Gemini Vision."""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        filename = secure_filename(file.filename)
        save_path = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(str(save_path))

        # Perform Gemini Vision analysis
        analysis_result = gemini_analyze_image(str(save_path))
        return jsonify({
            "filename": filename,
            "analysis": analysis_result,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/api/speak', methods=['POST'])
def speak_endpoint():
    """Trigger desktop TTS synthesis."""
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    if text:
        speak(text)
        return jsonify({"status": "spoken", "text": text})
    return jsonify({"error": "No text provided"}), 400

if __name__ == '__main__':
    print("Starting NOVA Backend API Server on http://127.0.0.1:5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
