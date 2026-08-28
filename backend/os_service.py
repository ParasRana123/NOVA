import webbrowser
import subprocess
from typing import Optional

try:
    import keyboard
except ImportError:
    keyboard = None

try:
    from AppOpener import open as appopen, close as appclose
except ImportError:
    appopen, appclose = None, None

try:
    from pywhatkit import playonyt
except ImportError:
    playonyt = None

def mute():
    if keyboard:
        keyboard.press_and_release('volume mute')

def unmute():
    if keyboard:
        keyboard.press_and_release('volume up')

def volume_up(steps: int = 10):
    if keyboard:
        for _ in range(steps):
            keyboard.press_and_release("volume up")

def volume_down(steps: int = 10):
    if keyboard:
        for _ in range(steps):
            keyboard.press_and_release("volume down")

def play_pause():
    if keyboard:
        keyboard.press_and_release("play/pause")

def next_track():
    if keyboard:
        keyboard.press_and_release("next track")

def previous_track():
    if keyboard:
        keyboard.press_and_release("previous track")

def take_screenshot():
    if keyboard:
        keyboard.press_and_release("print screen")

def find_text():
    if keyboard:
        keyboard.press_and_release("ctrl+f")

def close_active_window():
    if keyboard:
        keyboard.press_and_release("alt+f4")

def type_message(message: str):
    if keyboard:
        keyboard.write(message)

def handle_keyboard_action(command: str) -> bool:
    """Respond to keyboard action commands."""
    cmd = command.lower()
    if "increase" in cmd or "volume up" in cmd:
        volume_up()
    elif "decrease" in cmd or "volume down" in cmd:
        volume_down()
    elif "mute" in cmd:
        mute()
    elif "unmute" in cmd:
        unmute()
    elif "play" in cmd or "pause" in cmd:
        play_pause()
    elif "next track" in cmd:
        next_track()
    elif "previous track" in cmd:
        previous_track()
    elif "screenshot" in cmd:
        take_screenshot()
    elif "find" in cmd:
        find_text()
    elif "type" in cmd:
        type_message("NOVA")
    elif "close window" in cmd:
        close_active_window()
    else:
        return False
    return True

def open_application(app_name: str) -> bool:
    """Open desktop application using AppOpener."""
    if appopen and app_name:
        try:
            appopen(app_name.strip(), match_closest=True, output=True, throw_error=False)
            return True
        except Exception as e:
            print(f"[OSService] Error opening {app_name}: {e}")
    return False

def close_application(app_name: str) -> bool:
    """Close desktop application using AppOpener."""
    if appclose and app_name:
        try:
            appclose(app_name.strip(), match_closest=True, output=True, throw_error=False)
            return True
        except Exception as e:
            print(f"[OSService] Error closing {app_name}: {e}")
    return False

def search_youtube(query: str, play_first: bool = False):
    """Play directly on YouTube or open search results."""
    query = query.strip()
    if not query:
        return
    if play_first and playonyt:
        playonyt(query)
    else:
        search_url = f"https://www.youtube.com/results?search_query={query}"
        webbrowser.open(search_url)

def search_google(query: str):
    """Open Google search in the default web browser."""
    query = query.strip()
    if query:
        webbrowser.open(f"https://www.google.com/search?q={query}")

def search_amazon(query: str):
    """Open Amazon product search in the default web browser."""
    query = query.strip()
    if query:
        webbrowser.open(f"https://www.amazon.com/s?k={query}")

def open_file_in_notepad(file_path: str):
    """Open a text file in Notepad."""
    try:
        subprocess.Popen(["notepad.exe", str(file_path)])
    except Exception as e:
        print(f"[OSService] Error launching notepad: {e}")
