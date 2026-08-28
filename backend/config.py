import os
from pathlib import Path

# Project Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"
TASKS_DIR = BASE_DIR / "Tasks"

# Ensure essential directories exist
DATA_DIR.mkdir(exist_ok=True)
TASKS_DIR.mkdir(exist_ok=True)

# Attempt to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

# File Paths
CHATLOG_PATH = DATA_DIR / "chatlog.json"
TOKEN_PICKLE_PATH = BASE_DIR / "token.pickle"
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
GENERATED_CONTENT_PATH = BASE_DIR / "generated_content.txt"

# API Keys (Loaded from environment variables or .env file)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# AI Models & Assistant Settings
USER_NAME = os.getenv("USER_NAME", "Aditya")
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "NOVA")
GROQ_CHAT_MODEL = os.getenv("GROQ_CHAT_MODEL", "llama3-70b-8192")
GROQ_CONTENT_MODEL = os.getenv("GROQ_CONTENT_MODEL", "mixtral-8x7b-32768")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

# Calendar Scopes
CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']
