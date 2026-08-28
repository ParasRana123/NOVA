import os
import json
import re
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
    """Process voice or text prompt through NOVA's command router and Gemini LLM."""
    data = request.get_json() or {}
    user_text = data.get("query", "").strip()
    voice_enabled = data.get("speak", True)

    if not user_text:
        return jsonify({"error": "Empty query"}), 400

    cmd = user_text.lower().strip()
    command_type = "general_chat"
    response_text = ""

    try:
        # 1. YouTube Playback intent
        yt_match = re.search(r'^(?:play\s+(.+?)\s+on\s+youtube|play\s+(?:song|music|video)\s+(.+))$', cmd)
        if yt_match:
            command_type = "multimedia"
            query = (yt_match.group(1) or yt_match.group(2)).strip()
            search_youtube(query, play_first=True)
            response_text = f"Playing '{query}' on YouTube."

        # 2. Explicit Web Search intents
        elif re.search(r'^(?:search\s+(?:on\s+)?youtube\s+(?:for\s+)?|youtube\s+search\s+(?:for\s+)?)(.+)$', cmd):
            m = re.search(r'^(?:search\s+(?:on\s+)?youtube\s+(?:for\s+)?|youtube\s+search\s+(?:for\s+)?)(.+)$', cmd)
            command_type = "search"
            query = m.group(1).strip()
            search_youtube(query)
            response_text = f"Searched YouTube for: {query}"

        elif re.search(r'^(?:search\s+(?:on\s+)?google\s+(?:for\s+)?|google\s+search\s+(?:for\s+)?)(.+)$', cmd):
            m = re.search(r'^(?:search\s+(?:on\s+)?google\s+(?:for\s+)?|google\s+search\s+(?:for\s+)?)(.+)$', cmd)
            command_type = "search"
            query = m.group(1).strip()
            search_google(query)
            response_text = f"Searched Google for: {query}"

        elif re.search(r'^(?:search\s+(?:on\s+)?amazon\s+(?:for\s+)?|amazon\s+search\s+(?:for\s+)?)(.+)$', cmd):
            m = re.search(r'^(?:search\s+(?:on\s+)?amazon\s+(?:for\s+)?|amazon\s+search\s+(?:for\s+)?)(.+)$', cmd)
            command_type = "search"
            query = m.group(1).strip()
            search_amazon(query)
            response_text = f"Searched Amazon for: {query}"

        # 3. Content Drafting intent
        elif re.search(r'^(?:draft|write|compose|generate)\s+(?:an?\s+)?(?:email|letter|application|document|content)\s+(?:about|for|on)\s+(.+)$', cmd):
            m = re.search(r'^(?:draft|write|compose|generate)\s+(?:an?\s+)?(?:email|letter|application|document|content)\s+(?:about|for|on)\s+(.+)$', cmd)
            command_type = "content_drafting"
            topic = m.group(1).strip()
            response_text = generate_content(topic, auto_open=True)

        # 4. Reminders
        elif re.search(r'^(?:remind\s+me|set\s+(?:a\s+)?reminder)\b', cmd):
            success, msg = reminder(user_text)
            if success:
                command_type = "reminder"
                response_text = msg

        # 5. To-Do & Calendar commands
        if not response_text:
            todo_res = handle_todo_command(cmd)
            if todo_res:
                command_type = "todo_calendar"
                response_text = todo_res

        # 6. Application management
        if not response_text and re.search(r'^(?:open|launch)\s+([a-zA-Z0-9\s]+)$', cmd):
            m = re.search(r'^(?:open|launch)\s+([a-zA-Z0-9\s]+)$', cmd)
            app_name = m.group(1).strip()
            command_type = "app_management"
            open_application(app_name)
            response_text = f"Opening {app_name}"

        elif not response_text and re.search(r'^(?:close|quit|kill)\s+([a-zA-Z0-9\s]+)$', cmd):
            m = re.search(r'^(?:close|quit|kill)\s+([a-zA-Z0-9\s]+)$', cmd)
            app_name = m.group(1).strip()
            command_type = "app_management"
            close_application(app_name)
            response_text = f"Closed application {app_name}"

        # 7. OS Media / Keyboard macros
        elif not response_text and re.search(r'^(?:(?:increase|decrease|mute|unmute)\s+volume|mute|unmute|pause|resume|next\s+track|previous\s+track|take\s+a?\s*screenshot|screenshot)$', cmd):
            command_type = "os_control"
            handle_keyboard_action(cmd)
            response_text = f"Executed system command: {cmd}"

        # 8. All other queries -> Full Google Gemini conversational intelligence!
        if not response_text:
            command_type = "ai_chat"
            response_text = ai_chat(user_text)

        # Speak via desktop TTS if requested
        if voice_enabled and response_text and command_type in ["ai_chat", "multimedia", "reminder"]:
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
