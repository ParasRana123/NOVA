import os
import base64
import requests
from typing import Optional, Union
from pathlib import Path

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from backend.config import GEMINI_API_KEY, GEMINI_MODEL

DEFAULT_VISION_PROMPT = """
You are an Image Analyzer with expertise in identifying and understanding the contents of any given image. 
Provide a clear, structured analysis with:
1. Description of key objects, people, and scene elements (keep it concise).
2. Contextual insights or potential practical applications.
3. Suggestions for enhancement or further utilization.
"""

class VisionService:
    def __init__(self, api_key: str = GEMINI_API_KEY, model_name: str = GEMINI_MODEL):
        self.api_key = api_key
        self.model_name = model_name
        self.model = None
        self._setup()

    def _setup(self):
        if not self.api_key:
            from backend.config import GEMINI_API_KEY
            self.api_key = GEMINI_API_KEY

        if genai and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
            except Exception as e:
                print(f"[VisionService] Gemini SDK initialization error: {e}")
                self.model = None

    def analyze_image(self, image_input: Union[str, Path, bytes], prompt: Optional[str] = None) -> str:
        """
        Analyze an image file path or raw bytes using Google Gemini (SDK or REST fallback).
        """
        try:
            if isinstance(image_input, (str, Path)):
                file_path = Path(image_input)
                if not file_path.exists():
                    return f"Image file not found at {file_path}"
                with open(file_path, "rb") as f:
                    image_data = f.read()
                suffix = file_path.suffix.lower()
                mime_type = "image/png" if suffix == ".png" else "image/jpeg"
            else:
                image_data = image_input
                mime_type = "image/jpeg"

            analysis_prompt = prompt or DEFAULT_VISION_PROMPT

            # Try SDK if available
            if self.model:
                try:
                    image_part = {
                        "mime_type": mime_type,
                        "data": image_data
                    }
                    response = self.model.generate_content([analysis_prompt, image_part])
                    if response and hasattr(response, 'text') and response.text:
                        return response.text
                except Exception as e:
                    print(f"[VisionService] SDK call failed, trying REST fallback: {e}")

            # REST fallback
            if not self.api_key:
                from backend.config import GEMINI_API_KEY
                self.api_key = GEMINI_API_KEY

            if not self.api_key:
                return "Gemini API key is not configured. Please set GEMINI_API_KEY in .env."

            b64_img = base64.b64encode(image_data).decode("utf-8")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": analysis_prompt},
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": b64_img
                                }
                            }
                        ]
                    }
                ]
            }

            res = requests.post(url, json=payload, timeout=25)
            data = res.json()
            if res.status_code == 200:
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"]
                return "No analysis returned from Gemini."
            else:
                err = data.get("error", {}).get("message", res.text)
                return f"Gemini Vision API Error ({res.status_code}): {err}"

        except Exception as e:
            print(f"[VisionService] Error during image analysis: {e}")
            return f"Error analyzing image: {e}"

# Default instance and helper function
default_vision_service = VisionService()

def analyze_image(image_path: Union[str, Path], prompt: Optional[str] = None) -> str:
    return default_vision_service.analyze_image(image_path, prompt)
