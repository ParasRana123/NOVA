import os
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
        self._configured = False
        self._setup()

    def _setup(self):
        if genai and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                self._configured = True
            except Exception as e:
                print(f"[VisionService] Gemini initialization error: {e}")
                self._configured = False

    def analyze_image(self, image_input: Union[str, Path, bytes], prompt: Optional[str] = None) -> str:
        """
        Analyze an image file path or raw bytes using Google Gemini.
        """
        if not self._configured or not self.model:
            return "Gemini library is not installed or API is not configured. Please check your dependencies and API key."

        try:
            if isinstance(image_input, (str, Path)):
                file_path = Path(image_input)
                if not file_path.exists():
                    return f"Image file not found at {file_path}"
                with open(file_path, "rb") as f:
                    image_data = f.read()
                
                # Determine mime type from extension
                suffix = file_path.suffix.lower()
                mime_type = "image/png" if suffix == ".png" else "image/jpeg"
            else:
                image_data = image_input
                mime_type = "image/jpeg"

            image_part = {
                "mime_type": mime_type,
                "data": image_data
            }

            analysis_prompt = prompt or DEFAULT_VISION_PROMPT
            response = self.model.generate_content([analysis_prompt, image_part])
            return response.text if response and hasattr(response, 'text') else "No analysis returned."

        except Exception as e:
            print(f"[VisionService] Error during image analysis: {e}")
            return f"Error analyzing image: {e}"

# Default instance and helper function
default_vision_service = VisionService()

def analyze_image(image_path: Union[str, Path], prompt: Optional[str] = None) -> str:
    return default_vision_service.analyze_image(image_path, prompt)
