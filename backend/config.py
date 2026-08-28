import os
from pathlib import Path

# Project Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"
TASKS_DIR = BASE_DIR / "Tasks"

# Ensure essential directories exist
DATA_DIR.mkdir(exist_ok=True)
TASKS_DIR.mkdir(exist_ok=True)

# Function to parse .env file without external dependencies
def _load_env_file(path: Path):
    if not path.exists():
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception as e:
        print(f"[Config] Error parsing .env: {e}")

# Attempt to load .env file
_load_env_file(BASE_DIR / ".env")

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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# AI Models & Assistant Settings - Ultra Fast Flash Models
USER_NAME = os.getenv("USER_NAME", "Paras")
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "NOVA")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")
GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.1-flash-lite-preview")
GEMINI_CONTENT_MODEL = os.getenv("GEMINI_CONTENT_MODEL", "gemini-3.5-flash")
GEMINI_VISION_MODEL = os.getenv("GEMINI_VISION_MODEL", "gemini-3.1-flash-image-preview")

# Calendar Scopes
CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']
