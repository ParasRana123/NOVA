import json
import datetime
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from backend.config import (
    GEMINI_API_KEY, 
    GEMINI_CHAT_MODEL, 
    GEMINI_CONTENT_MODEL, 
    USER_NAME, 
    ASSISTANT_NAME, 
    CHATLOG_PATH, 
    GENERATED_CONTENT_PATH
)
from backend.weather_service import get_weather_by_city
from backend.os_service import open_file_in_notepad

# Fast candidate models for rapid conversational responses
FALLBACK_CHAT_MODELS = [
    GEMINI_CHAT_MODEL,
    "gemini-3.1-flash-lite-preview",
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-flash-latest"
]

class AIService:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.api_key = api_key
        self.session = requests.Session()
        self.model = None
        self.content_model = None
        self._setup()

    def _setup(self):
        if not self.api_key:
            from backend.config import GEMINI_API_KEY
            self.api_key = GEMINI_API_KEY

        if genai and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                system_instruction = (
                    f"Hello, I am {USER_NAME}. You are an accurate, advanced, and helpful AI assistant named {ASSISTANT_NAME}. "
                    "Provide responses in a professional, clear, concise, and structured tone using proper grammar."
                )
                self.model = genai.GenerativeModel(
                    model_name=GEMINI_CHAT_MODEL,
                    system_instruction=system_instruction
                )
                self.content_model = genai.GenerativeModel(
                    model_name=GEMINI_CONTENT_MODEL
                )
            except Exception as e:
                self.model = None
                self.content_model = None

    def load_chat_history(self) -> List[Dict[str, str]]:
        """Load conversation history from JSON storage."""
        if CHATLOG_PATH.exists():
            try:
                with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_chat_history(self, messages: List[Dict[str, str]]):
        """Persist conversation history to JSON storage."""
        try:
            with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
                json.dump(messages, f, indent=4)
        except IOError as e:
            print(f"[AIService] Error saving chat history: {e}")

    def get_realtime_context(self) -> str:
        """Construct current date/time context string for the LLM."""
        now = datetime.datetime.now()
        return (
            f"[Real-Time System Context: Day: {now.strftime('%A')}, Date: {now.strftime('%d %B %Y')}, Time: {now.strftime('%H:%M:%S')}]"
        )

    def clean_response(self, text: str) -> str:
        """Strip excess blank lines and system tags from generated text."""
        lines = text.split('\n')
        non_empty = [line.strip() for line in lines if line.strip()]
        return '\n'.join(non_empty).replace("</sys>", "")

    def _call_gemini_fast_api(self, contents: list, system_text: str, max_tokens: int = 512) -> str:
        """Execute fast Gemini API call with automatic model fallback."""
        if not self.api_key:
            from backend.config import GEMINI_API_KEY
            self.api_key = GEMINI_API_KEY

        if not self.api_key:
            return "Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file."

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": max_tokens
            }
        }
        if system_text:
            payload["system_instruction"] = {
                "parts": [{"text": system_text}]
            }

        # Try models in order until one responds quickly
        for model in FALLBACK_CHAT_MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            try:
                res = self.session.post(url, json=payload, timeout=8)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]
                elif res.status_code == 404:
                    # Model not available in this tier, try next fallback
                    continue
                else:
                    data = res.json()
                    error_msg = data.get("error", {}).get("message", res.text)
                    return f"Gemini API Error ({res.status_code}): {error_msg}"
            except Exception as e:
                # On timeout or connection error, try next fast fallback
                continue

        return "Gemini is currently taking longer than expected to respond. Please try again."

    def chat(self, prompt: str) -> str:
        """Send prompt to Google Gemini with context and conversation history."""
        history = self.load_chat_history()
        history.append({"role": "user", "content": prompt})

        # Inject real-time context (weather or date/time)
        if "weather" in prompt.lower() and " in " in prompt.lower():
            city = prompt.lower().split(" in ")[-1].strip()
            context_content = f"[Current Weather Context: {get_weather_by_city(city)}]"
        else:
            context_content = self.get_realtime_context()

        # Build contents structure from history
        contents = []
        for item in history[-6:-1]:
            role = "user" if item.get("role") == "user" else "model"
            content_text = item.get("content", "")
            if content_text:
                contents.append({"role": role, "parts": [{"text": content_text}]})

        full_user_prompt = f"{context_content}\n\n{prompt}"
        contents.append({"role": "user", "parts": [{"text": full_user_prompt}]})

        system_instruction = (
            f"Hello, I am {USER_NAME}. You are an accurate, advanced, and helpful AI assistant named {ASSISTANT_NAME}. "
            "Provide responses in a professional, clear, concise, and helpful tone using proper grammar."
        )

        answer = self._call_gemini_fast_api(contents, system_instruction, max_tokens=512)

        cleaned_answer = self.clean_response(answer)
        history.append({"role": "assistant", "content": cleaned_answer})
        self.save_chat_history(history)
        return cleaned_answer

    def generate_content(self, topic: str, auto_open: bool = True) -> str:
        """Generate formatted email/document content using Gemini and save to file."""
        prompt_instruction = (
            "You are a professional writing assistant. Draft high-quality, clearly structured, and formatted content "
            f"for the following topic:\n\n{topic}"
        )
        contents = [{"role": "user", "parts": [{"text": prompt_instruction}]}]

        result = self._call_gemini_fast_api(contents, "", max_tokens=1500)
        cleaned = self.clean_response(result)

        # Save content to text file
        with open(GENERATED_CONTENT_PATH, "w", encoding="utf-8") as f:
            f.write(cleaned)

        if auto_open:
            open_file_in_notepad(str(GENERATED_CONTENT_PATH))

        return cleaned

# Global instance and module-level helper functions
default_ai_service = AIService()

def chat(prompt: str) -> str:
    return default_ai_service.chat(prompt)

def generate_content(topic: str, auto_open: bool = True) -> str:
    return default_ai_service.generate_content(topic, auto_open)
