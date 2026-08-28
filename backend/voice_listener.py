import threading
from typing import Callable, Optional

try:
    import speech_recognition as sr
except ImportError:
    sr = None

from backend.speech_service import default_speech_service, speak

class VoiceListener:
    def __init__(self, on_command_callback: Optional[Callable[[str], None]] = None, on_status_update: Optional[Callable[[str], None]] = None):
        self.on_command_callback = on_command_callback
        self.on_status_update = on_status_update
        self.stop_flag = False
        if sr:
            self.recognizer = sr.Recognizer()
            self.recognizer.dynamic_energy_threshold = True
        else:
            self.recognizer = None

    def _update_status(self, text: str):
        if self.on_status_update:
            self.on_status_update(text)

    def listen_continuous(self):
        """Continuously listen for spoken commands until stop_flag is True."""
        if not sr or not self.recognizer:
            self._update_status("SpeechRecognition is not installed.")
            return

        while not self.stop_flag:
            if default_speech_service.speaking_flag:
                continue

            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self._update_status("NOVA: Listening for your command...")

                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    if self.stop_flag:
                        break

                    command = self.recognizer.recognize_google(audio).lower()
                    self._update_status(f"Recognized: {command}")

                    if self.on_command_callback:
                        threading.Thread(target=self.on_command_callback, args=(command,), daemon=True).start()

            except sr.UnknownValueError:
                if not default_speech_service.speaking_flag:
                    self._update_status("NOVA: I couldn't understand that. Please try again.")
            except sr.WaitTimeoutError:
                pass
            except sr.RequestError:
                if not default_speech_service.speaking_flag:
                    self._update_status("NOVA: Issue with the speech recognition service.")
            except Exception as e:
                if not default_speech_service.speaking_flag:
                    self._update_status(f"NOVA: Error: {e}")

    def listen_wake_word(self, wake_words=("hey nova", "nova")):
        """Listen for wake word before transitioning to active listening."""
        if not sr or not self.recognizer:
            self._update_status("SpeechRecognition is not installed.")
            return

        speak("Hello. Say 'Hey NOVA' when you need me.")
        while not self.stop_flag:
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self._update_status("Listening for wake word...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    command = self.recognizer.recognize_google(audio).lower()

                    if any(w in command for w in wake_words):
                        speak("Yes! How can I assist you?")
                        self.listen_continuous()
                        break
            except (sr.UnknownValueError, sr.WaitTimeoutError):
                continue
            except Exception as e:
                print(f"[VoiceListener] Wake word listener error: {e}")

    def start_in_background(self, target_method: str = "continuous"):
        """Launch the listener in a background daemon thread."""
        self.stop_flag = False
        target = self.listen_continuous if target_method == "continuous" else self.listen_wake_word
        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        return thread

    def stop(self):
        """Signal the listener loop to stop."""
        self.stop_flag = True
