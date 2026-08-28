import json
import datetime
from typing import List, Dict, Any, Optional

try:
    from groq import Groq
except ImportError:
    Groq = None

from backend.config import (
    GROQ_API_KEY, 
    GROQ_CHAT_MODEL, 
    GROQ_CONTENT_MODEL, 
    USER_NAME, 
    ASSISTANT_NAME, 
    CHATLOG_PATH, 
    GENERATED_CONTENT_PATH
)
from backend.weather_service import get_weather_by_city
from backend.os_service import open_file_in_notepad

class AIService:
    def __init__(self, api_key: str = GROQ_API_KEY):
        self.api_key = api_key
        self.client = Groq(api_key=self.api_key) if (Groq and self.api_key) else None
        self.system_prompt = (
            f"Hello, I am {USER_NAME}. You are an accurate and advanced AI chatbot named {ASSISTANT_NAME}. "
            "Provide answers in a professional, concise, and helpful tone using proper grammar."
        )

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
            f"Current Real-Time Context:\n"
            f"Day: {now.strftime('%A')}, Date: {now.strftime('%d %B %Y')}, Time: {now.strftime('%H:%M:%S')}"
        )

    def clean_response(self, text: str) -> str:
        """Strip excess blank lines and system tags from generated text."""
        lines = text.split('\n')
        non_empty = [line.strip() for line in lines if line.strip()]
        return '\n'.join(non_empty).replace("</sys>", "")

    def chat(self, prompt: str) -> str:
        """Send prompt to Groq LLaMA-3 with context and conversation history."""
        if not self.client:
            return "Groq client is not installed or configured. Please install 'groq' and check your API key."

        history = self.load_chat_history()
        history.append({"role": "user", "content": prompt})

        # Inject real-time context (weather or date/time)
        if "weather" in prompt.lower() and " in " in prompt.lower():
            city = prompt.lower().split(" in ")[-1].strip()
            context_content = get_weather_by_city(city)
        else:
            context_content = self.get_realtime_context()

        system_context = {"role": "system", "content": context_content}
        messages_payload = [{"role": "system", "content": self.system_prompt}, system_context] + history[-10:]

        try:
            completion = self.client.chat.completions.create(
                model=GROQ_CHAT_MODEL,
                messages=messages_payload,
                max_tokens=1024,
                temperature=0.7,
                top_p=1,
                stream=True
            )

            answer = ""
            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    answer += chunk.choices[0].delta.content

            cleaned_answer = self.clean_response(answer)
            history.append({"role": "assistant", "content": cleaned_answer})
            self.save_chat_history(history)
            return cleaned_answer

        except Exception as e:
            print(f"[AIService] Chat error: {e}")
            return f"An error occurred while generating a response: {e}"

    def generate_content(self, topic: str, auto_open: bool = True) -> str:
        """Generate formatted email/document content using Mixtral and save to file."""
        if not self.client:
            return "Groq client is not installed or configured."

        prompt_messages = [
            {"role": "system", "content": "You are a professional writing assistant. Draft clear, high-quality, formatted content."},
            {"role": "user", "content": f"Please draft content for the following topic: {topic}"}
        ]

        try:
            completion = self.client.chat.completions.create(
                model=GROQ_CONTENT_MODEL,
                messages=prompt_messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stream=True
            )

            result = ""
            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    result += chunk.choices[0].delta.content

            cleaned = self.clean_response(result)

            # Save content to text file
            with open(GENERATED_CONTENT_PATH, "w", encoding="utf-8") as f:
                f.write(cleaned)

            if auto_open:
                open_file_in_notepad(str(GENERATED_CONTENT_PATH))

            return cleaned
        except Exception as e:
            print(f"[AIService] Content generation error: {e}")
            return f"Error generating content: {e}"

# Global instance and module-level helper functions
default_ai_service = AIService()

def chat(prompt: str) -> str:
    return default_ai_service.chat(prompt)

def generate_content(topic: str, auto_open: bool = True) -> str:
    return default_ai_service.generate_content(topic, auto_open)
