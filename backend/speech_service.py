import re
import threading
from typing import Optional

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

def clean_speech_text(text: str) -> str:
    """Strip markdown symbols (#, *, _, `, ~, ---) so TTS doesn't vocalize syntax."""
    if not text:
        return ""
    clean = re.sub(r'[*#_`~]', '', text)
    clean = re.sub(r'^[•\-\+]\s+', '', clean, flags=re.MULTILINE)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

class SpeechService:
    def __init__(self, rate: int = 220, voice_index: int = 1):
        self.rate = rate
        self.voice_index = voice_index
        self._lock = threading.Lock()
        self.speaking_flag = False
        self.speak_enabled = True
        self.engine = self._init_engine()

    def _init_engine(self):
        if not pyttsx3:
            return None
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            if voices and len(voices) > self.voice_index:
                engine.setProperty("voice", voices[self.voice_index].id)
            elif voices:
                engine.setProperty("voice", voices[0].id)
            engine.setProperty("rate", self.rate)
            return engine
        except Exception as e:
            print(f"[SpeechService] Warning initializing pyttsx3: {e}")
            return None

    def speak(self, text: str, block: bool = True):
        if not self.speak_enabled or not text:
            return

        speech_text = clean_speech_text(text)
        print(f"[NOVA Voice]: {speech_text}")
        if block:
            self._speak_internal(speech_text)
        else:
            threading.Thread(target=self._speak_internal, args=(speech_text,), daemon=True).start()

    def _speak_internal(self, text: str):
        with self._lock:
            self.speaking_flag = True
            try:
                engine = self._init_engine()
                if engine:
                    engine.say(text)
                    engine.runAndWait()
            except Exception as e:
                print(f"[SpeechService] Error during speech synthesis: {e}")
            finally:
                self.speaking_flag = False

    def stop(self):
        if self.engine:
            try:
                self.engine.stop()
            except Exception:
                pass

# Global default instance and helper functions for backward compatibility
default_speech_service = SpeechService()

def setup_nova(rate: int = 240, voice_index: int = 1):
    return default_speech_service._init_engine()

def speak(engine_or_text, text=None):
    if text is None:
        message = str(engine_or_text)
    else:
        message = str(text)
    default_speech_service.speak(message)
