"""
NOVA Backend Package
Exposes core virtual assistant functionalities including AI chat, Computer Vision,
Voice/TTS, Calendar, To-Do lists, OS controls, Reminders, and Weather.
"""

from backend.config import (
    BASE_DIR,
    DATA_DIR,
    TASKS_DIR,
    CHATLOG_PATH,
    GROQ_API_KEY,
    GEMINI_API_KEY,
    OPENWEATHER_API_KEY,
    USER_NAME,
    ASSISTANT_NAME
)

from backend.speech_service import (
    SpeechService,
    default_speech_service,
    setup_nova,
    speak
)

from backend.weather_service import (
    get_location_by_ip,
    get_weather,
    get_weather_by_city
)

from backend.os_service import (
    handle_keyboard_action,
    open_application,
    close_application,
    search_youtube,
    search_google,
    search_amazon,
    open_file_in_notepad
)

from backend.reminder_service import (
    reminder,
    trigger_reminder
)

from backend.ai_service import (
    AIService,
    default_ai_service,
    chat,
    generate_content
)

from backend.vision_service import (
    VisionService,
    default_vision_service,
    analyze_image
)

from backend.calendar_service import (
    CalendarService,
    default_calendar_service
)

from backend.todo_service import (
    add_task,
    remove_task,
    get_tasks,
    sort_tasks,
    search_tasks,
    get_tasks_by_priority,
    get_upcoming_calendar_events,
    handle_todo_command,
    todomain
)

from backend.voice_listener import (
    VoiceListener
)

__all__ = [
    # Config
    "BASE_DIR",
    "DATA_DIR",
    "TASKS_DIR",
    "CHATLOG_PATH",
    "GROQ_API_KEY",
    "GEMINI_API_KEY",
    "OPENWEATHER_API_KEY",
    "USER_NAME",
    "ASSISTANT_NAME",
    # Speech
    "SpeechService",
    "default_speech_service",
    "setup_nova",
    "speak",
    # Weather & Location
    "get_location_by_ip",
    "get_weather",
    "get_weather_by_city",
    # OS & System
    "handle_keyboard_action",
    "open_application",
    "close_application",
    "search_youtube",
    "search_google",
    "search_amazon",
    "open_file_in_notepad",
    # Reminders
    "reminder",
    "trigger_reminder",
    # AI & LLM
    "AIService",
    "default_ai_service",
    "chat",
    "generate_content",
    # Vision
    "VisionService",
    "default_vision_service",
    "analyze_image",
    # Calendar & Tasks
    "CalendarService",
    "default_calendar_service",
    "add_task",
    "remove_task",
    "get_tasks",
    "sort_tasks",
    "search_tasks",
    "get_tasks_by_priority",
    "get_upcoming_calendar_events",
    "handle_todo_command",
    "todomain",
    # Voice Listener
    "VoiceListener"
]
