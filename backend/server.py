import os
import sys
import json
import re
from pathlib import Path

# Ensure root directory is on python search path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import NOVA backend services
from backend.config import CHATLOG_PATH, OPENWEATHER_API_KEY
from backend.speech_service import speak, default_speech_service
from backend.weather_service import get_location_by_ip, get_weather, get_weather_by_city
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
    search_amazon,
    get_supported_commands_guide,
    get_app_action_payload
)

app = Flask(__name__)

# Enable Cross-Origin Resource Sharing globally
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

@app.after_request
def add_cors_headers(response):
    """Ensure CORS headers are present on every response including errors and preflight."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept'
    return response

UPLOAD_FOLDER = BASE_DIR / "Data" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'HEAD', 'OPTIONS'])
@app.route('/api', methods=['GET', 'HEAD', 'OPTIONS'])
def root_status():
    if request.method == 'OPTIONS':
        return make_response("", 204)
    return jsonify({
        "message": "NOVA Virtual Assistant API is running.",
        "assistant": "NOVA",
        "version": "2.0.0",
        "status": "online",
        "endpoints": [
            "/api/health",
            "/api/chat",
            "/api/weather",
            "/api/chat-history",
            "/api/analyze-image",
            "/api/speak"
        ]
    })

@app.route('/health', methods=['GET', 'HEAD', 'OPTIONS'])
@app.route('/api/health', methods=['GET', 'HEAD', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return make_response("", 204)
    return jsonify({
        "status": "healthy",
        "assistant": "NOVA",
        "version": "2.0.0"
    })

@app.route('/api/weather', methods=['GET', 'OPTIONS'])
def get_weather_telemetry():
    """Fetch current location and weather details."""
    if request.method == 'OPTIONS':
        return make_response("", 204)
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

@app.route('/api/chat-history', methods=['GET', 'OPTIONS'])
def get_chat_history():
    """Return stored chat history from chatlog.json."""
    if request.method == 'OPTIONS':
        return make_response("", 204)
    try:
        if CHATLOG_PATH.exists():
            with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
                history = json.load(f)
            return jsonify({"history": history})
        return jsonify({"history": []})
    except Exception as e:
        return jsonify({"error": str(e), "history": []}), 500

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def process_chat():
    """Process voice or text prompt through NOVA's full command suite and Gemini LLM."""
    if request.method == 'OPTIONS':
        return make_response("", 204)

    data = request.get_json() or {}
    user_text = data.get("query", "").strip()
    voice_enabled = data.get("speak", True)

    if not user_text:
        return jsonify({"error": "Empty query"}), 400

    # Normalize command (strip punctuation, lower-case, remove conversational prefixes like "hey nova", "please")
    cmd = user_text.lower().strip().rstrip(".,!?")
    clean_cmd = re.sub(r'^(?:hey\s+nova,?\s*|nova,?\s*|innova,?\s*|please\s+|can\s+you\s+)', '', cmd).strip()
    command_type = "general_chat"
    response_text = ""
    action = None

    try:
        # 0. Help / Supported Commands
        if re.search(r'^(?:help|what\s+commands\s+do\s+you\s+support|what\s+can\s+you\s+do|commands\s+list|list\s+of\s+commands)$', clean_cmd):
            command_type = "help"
            response_text = get_supported_commands_guide()

        # 1. Application Opening (e.g. "open whatsapp", "launch chrome", "open notepad")
        elif re.search(r'^(?:open|launch|start)\s+([a-zA-Z0-9\s\.\-_]+)$', clean_cmd):
            m = re.search(r'^(?:open|launch|start)\s+([a-zA-Z0-9\s\.\-_]+)$', clean_cmd)
            app_name = m.group(1).strip()
            command_type = "app_management"
            action = get_app_action_payload(app_name)
            success = open_application(app_name)
            response_text = f"Opening {app_name} on your device." if success else f"Opening {app_name}."

        # 2. Application Closing (e.g. "close whatsapp", "kill chrome")
        elif re.search(r'^(?:close|quit|kill|stop)\s+([a-zA-Z0-9\s\.\-_]+)$', clean_cmd) and "window" not in clean_cmd:
            m = re.search(r'^(?:close|quit|kill|stop)\s+([a-zA-Z0-9\s\.\-_]+)$', clean_cmd)
            app_name = m.group(1).strip()
            command_type = "app_management"
            close_application(app_name)
            response_text = f"Closed {app_name}."

        # 3. YouTube Music & Playback
        elif re.search(r'^(?:play\s+(.+?)\s+on\s+youtube|play\s+(?:song|music|video)\s+(.+)|play\s+(.+))$', clean_cmd):
            m = re.search(r'^(?:play\s+(.+?)\s+on\s+youtube|play\s+(?:song|music|video)\s+(.+)|play\s+(.+))$', clean_cmd)
            query = (m.group(1) or m.group(2) or m.group(3)).strip()
            if query and query not in ["music", "song", "pause", "resume"]:
                command_type = "multimedia"
                action = {"type": "open_url", "url": f"https://www.youtube.com/results?search_query={query}"}
                search_youtube(query, play_first=True)
                response_text = f"Playing '{query}' on YouTube."

        # 4. Explicit Web Searches (Google, YouTube, Amazon)
        elif re.search(r'^(?:search\s+(?:on\s+)?youtube\s+(?:for\s+)?|youtube\s+search\s+(?:for\s+)?|youtube\s+)(.+)$', clean_cmd):
            m = re.search(r'^(?:search\s+(?:on\s+)?youtube\s+(?:for\s+)?|youtube\s+search\s+(?:for\s+)?|youtube\s+)(.+)$', clean_cmd)
            query = m.group(1).strip()
            command_type = "search"
            action = {"type": "open_url", "url": f"https://www.youtube.com/results?search_query={query}"}
            search_youtube(query)
            response_text = f"Searched YouTube for: {query}"

        elif re.search(r'^(?:search\s+(?:on\s+)?google\s+(?:for\s+)?|google\s+search\s+(?:for\s+)?|google\s+)(.+)$', clean_cmd):
            m = re.search(r'^(?:search\s+(?:on\s+)?google\s+(?:for\s+)?|google\s+search\s+(?:for\s+)?|google\s+)(.+)$', clean_cmd)
            query = m.group(1).strip()
            command_type = "search"
            action = {"type": "open_url", "url": f"https://www.google.com/search?q={query}"}
            search_google(query)
            response_text = f"Searched Google for: {query}"

        elif re.search(r'^(?:search\s+(?:on\s+)?amazon\s+(?:for\s+)?|amazon\s+search\s+(?:for\s+)?|amazon\s+|buy\s+(.+?)\s+on\s+amazon)(.+)?$', clean_cmd):
            m = re.search(r'^(?:search\s+(?:on\s+)?amazon\s+(?:for\s+)?|amazon\s+search\s+(?:for\s+)?|amazon\s+|buy\s+(.+?)\s+on\s+amazon)(.+)?$', clean_cmd)
            query = (m.group(1) or m.group(2) or "").strip()
            command_type = "search"
            action = {"type": "open_url", "url": f"https://www.amazon.com/s?k={query}"}
            search_amazon(query)
            response_text = f"Searching Amazon for: {query}"

        # 5. Content Drafting (Emails, Letters, Applications, Documents)
        elif re.search(r'^(?:draft|write|compose|generate)\s+(?:an?\s+)?(?:email|letter|application|document|content)\s+(?:about|for|on)\s+(.+)$', clean_cmd) or clean_cmd.startswith("content ") or clean_cmd.startswith("email "):
            topic = re.sub(r'^(?:draft|write|compose|generate)\s+(?:an?\s+)?(?:email|letter|application|document|content)\s+(?:about|for|on)\s+|^(?:content|email)\s+', '', clean_cmd).strip()
            if topic:
                command_type = "content_drafting"
                response_text = generate_content(topic, auto_open=True)

        # 6. Reminders
        elif re.search(r'^(?:remind\s+me|set\s+(?:a\s+)?reminder)\b', clean_cmd):
            success, msg = reminder(clean_cmd)
            if success:
                command_type = "reminder"
                response_text = msg

        # 7. To-Do, Priority Lists & Google Calendar
        if not response_text:
            todo_res = handle_todo_command(clean_cmd)
            if todo_res:
                command_type = "todo_calendar"
                response_text = todo_res

        # 8. OS Media / Volume / Keyboard Macros
        if not response_text and re.search(r'^(?:(?:increase|decrease|raise|lower|turn\s+up|turn\s+down|mute|unmute)\s+(?:volume|sound|audio)|mute|unmute|pause|resume|next\s+track|next\s+song|previous\s+track|previous\s+song|take\s+a?\s*screenshot|screenshot|find|close\s+window)$', clean_cmd):
            command_type = "os_control"
            handle_keyboard_action(clean_cmd)
            response_text = f"Executed system action: {clean_cmd}"

        # 9. Time & Date Telemetry
        elif not response_text and re.search(r'^(?:what\s+time\s+is\s+it|what\s+is\s+the\s+time|current\s+time|time)$', clean_cmd):
            import datetime
            now = datetime.datetime.now()
            command_type = "telemetry"
            response_text = f"The current time is {now.strftime('%I:%M:%S %p')} on {now.strftime('%A, %B %d, %Y')}."

        # 10. Direct Weather Query (e.g. "weather in Tokyo", "what is the weather")
        elif not response_text and re.search(r'^(?:weather\s+in\s+([a-zA-Z\s]+)|what\s+is\s+the\s+weather|weather)$', clean_cmd):
            m = re.search(r'^(?:weather\s+in\s+([a-zA-Z\s]+)|what\s+is\s+the\s+weather|weather)$', clean_cmd)
            city = m.group(1).strip() if m and m.group(1) else ""
            command_type = "weather"
            if city:
                response_text = get_weather_by_city(city)
            else:
                loc, lat, lon = get_location_by_ip()
                response_text = get_weather(lat, lon, OPENWEATHER_API_KEY)

        # 11. Exit / Quit
        elif not response_text and re.search(r'^(?:goodbye|bye|sleep|exit|quit|that\'s\s+it)$', clean_cmd):
            command_type = "system"
            response_text = "Goodbye, Sir. Have a great day!"

        # 12. Fallback to Google Gemini (Full General Intelligence)
        if not response_text:
            command_type = "ai_chat"
            response_text = ai_chat(user_text)

        # Spoken audio via desktop TTS (if running in desktop environment)
        if voice_enabled and response_text and command_type in ["ai_chat", "multimedia", "reminder", "app_management", "telemetry", "weather", "system"]:
            try:
                default_speech_service.speak(response_text, block=False)
            except Exception:
                pass

        return jsonify({
            "query": user_text,
            "response": response_text,
            "command_type": command_type,
            "action": action,
            "status": "success"
        })

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/api/analyze-image', methods=['POST', 'OPTIONS'])
def analyze_image_endpoint():
    """Analyze uploaded image using Gemini Vision."""
    if request.method == 'OPTIONS':
        return make_response("", 204)
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        filename = secure_filename(file.filename)
        save_path = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(str(save_path))

        analysis_result = gemini_analyze_image(str(save_path))
        return jsonify({
            "filename": filename,
            "analysis": analysis_result,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/api/speak', methods=['POST', 'OPTIONS'])
def speak_endpoint():
    """Trigger desktop TTS synthesis."""
    if request.method == 'OPTIONS':
        return make_response("", 204)
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    if text:
        speak(text)
        return jsonify({"status": "spoken", "text": text})
    return jsonify({"error": "No text provided"}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Endpoint not found",
        "status": 404,
        "available_endpoints": [
            "/",
            "/api/health",
            "/api/chat",
            "/api/weather",
            "/api/chat-history",
            "/api/analyze-image",
            "/api/speak"
        ]
    }), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting NOVA Backend API Server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
