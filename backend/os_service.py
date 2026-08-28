import os
import sys
import webbrowser
import subprocess
import re
from typing import Optional, Dict, Any

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

# Known Windows app protocol schemes and executable aliases (for local desktop execution)
WINDOWS_APP_PROTOCOLS = {
    "whatsapp": ["start whatsapp:", "start whatsapp", "https://web.whatsapp.com"],
    "calculator": ["calc.exe", "start calc:"],
    "calc": ["calc.exe", "start calc:"],
    "notepad": ["notepad.exe"],
    "settings": ["start ms-settings:"],
    "chrome": ["start chrome", "chrome.exe"],
    "google chrome": ["start chrome", "chrome.exe"],
    "edge": ["start msedge", "msedge.exe"],
    "spotify": ["start spotify:", "spotify.exe"],
    "camera": ["start microsoft.windows.camera:"],
    "explorer": ["start explorer"],
    "file explorer": ["start explorer"],
    "files": ["start explorer"],
    "cmd": ["cmd.exe"],
    "command prompt": ["cmd.exe"],
    "terminal": ["powershell.exe", "wt.exe", "cmd.exe"],
    "powershell": ["powershell.exe"],
    "vs code": ["code", "start code"],
    "vscode": ["code", "start code"],
    "word": ["start winword"],
    "excel": ["start excel"],
    "powerpoint": ["start powerpnt"],
    "paint": ["mspaint.exe"],
    "task manager": ["taskmgr.exe"],
}

# Native OS URI schemes that open the installed desktop / mobile application directly
APP_NATIVE_PROTOCOLS = {
    "whatsapp": "whatsapp://",
    "spotify": "spotify://",
    "vscode": "vscode://",
    "vs code": "vscode://",
    "discord": "discord://",
    "telegram": "tg://",
    "calculator": "calc:",
    "calc": "calc:",
    "settings": "ms-settings:",
    "camera": "microsoft.windows.camera:",
    "calendar": "outlookcal:",
    "mail": "mailto:",
    "gmail": "mailto:",
    "maps": "bingmaps:?",
    "photos": "ms-photos:",
    "clock": "ms-clock:",
    "alarms": "ms-clock:",
    "store": "ms-windows-store:",
    "zoom": "zoommtg://",
    "slack": "slack://",
}

# Web URL fallbacks
APP_WEB_URLS = {
    "whatsapp": "https://web.whatsapp.com",
    "spotify": "https://open.spotify.com",
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "chrome": "https://www.google.com",
    "edge": "https://www.bing.com",
    "calculator": "https://www.google.com/search?q=calculator",
    "calc": "https://www.google.com/search?q=calculator",
    "notepad": "https://editpad.org",
    "gmail": "https://mail.google.com",
    "mail": "https://mail.google.com",
    "github": "https://github.com",
    "vs code": "https://vscode.dev",
    "vscode": "https://vscode.dev",
    "discord": "https://discord.com/app",
    "telegram": "https://web.telegram.org",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "instagram": "https://www.instagram.com",
    "reddit": "https://www.reddit.com",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "chatgpt": "https://chat.openai.com",
    "gemini": "https://gemini.google.com",
    "notion": "https://www.notion.so",
    "calendar": "https://calendar.google.com",
    "maps": "https://maps.google.com",
    "drive": "https://drive.google.com",
    "settings": "ms-settings:"
}

def get_app_action_payload(app_name: str) -> Dict[str, Any]:
    """Return protocol URI for native app opening and fallback web URL."""
    clean = app_name.lower().strip().rstrip(".,!?")
    protocol = None
    web_url = None

    for k, v in APP_NATIVE_PROTOCOLS.items():
        if k == clean or k in clean or clean in k:
            protocol = v
            break

    for k, v in APP_WEB_URLS.items():
        if k == clean or k in clean or clean in k:
            web_url = v
            break

    if not web_url:
        web_url = f"https://www.google.com/search?q={clean}"

    return {
        "type": "open_app",
        "app": clean,
        "protocol": protocol,
        "url": web_url
    }

def mute():
    if keyboard:
        try:
            keyboard.press_and_release('volume mute')
        except Exception:
            pass

def unmute():
    if keyboard:
        try:
            keyboard.press_and_release('volume up')
        except Exception:
            pass

def volume_up(steps: int = 10):
    if keyboard:
        try:
            for _ in range(steps):
                keyboard.press_and_release("volume up")
        except Exception:
            pass

def volume_down(steps: int = 10):
    if keyboard:
        try:
            for _ in range(steps):
                keyboard.press_and_release("volume down")
        except Exception:
            pass

def play_pause():
    if keyboard:
        try:
            keyboard.press_and_release("play/pause")
        except Exception:
            pass

def next_track():
    if keyboard:
        try:
            keyboard.press_and_release("next track")
        except Exception:
            pass

def previous_track():
    if keyboard:
        try:
            keyboard.press_and_release("previous track")
        except Exception:
            pass

def take_screenshot():
    if keyboard:
        try:
            keyboard.press_and_release("print screen")
        except Exception:
            pass

def find_text():
    if keyboard:
        try:
            keyboard.press_and_release("ctrl+f")
        except Exception:
            pass

def close_active_window():
    if keyboard:
        try:
            keyboard.press_and_release("alt+f4")
        except Exception:
            pass

def type_message(message: str):
    if keyboard:
        try:
            keyboard.write(message)
        except Exception:
            pass

def handle_keyboard_action(command: str) -> bool:
    """Respond to keyboard action commands."""
    cmd = command.lower().strip()
    if any(k in cmd for k in ["increase", "volume up", "raise volume", "louder"]):
        volume_up()
    elif any(k in cmd for k in ["decrease", "volume down", "lower volume", "quieter"]):
        volume_down()
    elif "unmute" in cmd:
        unmute()
    elif "mute" in cmd:
        mute()
    elif any(k in cmd for k in ["play", "pause", "resume"]):
        play_pause()
    elif any(k in cmd for k in ["next track", "next song", "skip track"]):
        next_track()
    elif any(k in cmd for k in ["previous track", "previous song"]):
        previous_track()
    elif any(k in cmd for k in ["screenshot", "capture screen"]):
        take_screenshot()
    elif "find" in cmd:
        find_text()
    elif cmd.startswith("type "):
        type_message(cmd.replace("type ", "", 1))
    elif "close window" in cmd or "close active window" in cmd:
        close_active_window()
    else:
        return False
    return True

def open_application(app_name: str) -> bool:
    """Open desktop application using protocol schemes, AppOpener, and executables."""
    clean_app = app_name.lower().strip().rstrip(".,!?")
    if not clean_app:
        return False

    # Check known Windows protocols
    if clean_app in WINDOWS_APP_PROTOCOLS:
        commands = WINDOWS_APP_PROTOCOLS[clean_app]
        for cmd in commands:
            try:
                if cmd.startswith("http"):
                    webbrowser.open(cmd)
                    return True
                elif cmd.startswith("start "):
                    os.system(cmd)
                    return True
                else:
                    subprocess.Popen(cmd, shell=True)
                    return True
            except Exception:
                continue

    # Try AppOpener
    if appopen:
        try:
            appopen(clean_app, match_closest=True, output=True, throw_error=False)
            return True
        except Exception:
            pass

    # Try standard start command
    try:
        os.system(f"start {clean_app}")
        return True
    except Exception as e:
        print(f"[OSService] Error launching {clean_app}: {e}")
        return False

def close_application(app_name: str) -> bool:
    """Close desktop application using AppOpener and taskkill."""
    clean_app = app_name.lower().strip().rstrip(".,!?")
    if not clean_app:
        return False

    # Try AppOpener
    if appclose:
        try:
            appclose(clean_app, match_closest=True, output=True, throw_error=False)
            return True
        except Exception:
            pass

    # Try taskkill
    try:
        os.system(f"taskkill /f /im {clean_app}.exe 2>nul")
        return True
    except Exception as e:
        print(f"[OSService] Error closing {clean_app}: {e}")
        return False

def search_youtube(query: str, play_first: bool = False):
    """Play directly on YouTube or open search results."""
    clean_query = query.strip().rstrip(".,!?")
    if not clean_query:
        return
    if play_first and playonyt:
        try:
            playonyt(clean_query)
            return
        except Exception:
            pass
    search_url = f"https://www.youtube.com/results?search_query={clean_query}"
    webbrowser.open(search_url)

def search_google(query: str):
    """Open Google search in the default web browser."""
    clean_query = query.strip().rstrip(".,!?")
    if clean_query:
        webbrowser.open(f"https://www.google.com/search?q={clean_query}")

def search_amazon(query: str):
    """Open Amazon product search in the default web browser."""
    clean_query = query.strip().rstrip(".,!?")
    if clean_query:
        webbrowser.open(f"https://www.amazon.com/s?k={clean_query}")

def open_file_in_notepad(file_path: str):
    """Open a text file in Notepad."""
    try:
        subprocess.Popen(["notepad.exe", str(file_path)])
    except Exception as e:
        print(f"[OSService] Error launching notepad: {e}")

def get_supported_commands_guide() -> str:
    """Return a comprehensive guide of all supported commands."""
    return """✨ **NOVA Supported Commands Guide**

🎛️ **App & OS Control:**
• `Open <app>` (e.g. *Open WhatsApp*, *Open Spotify*, *Open Calculator*, *Open Chrome*, *Open VS Code*, *Open Settings*)
• `Close <app>` (e.g. *Close WhatsApp*, *Close Chrome*, *Close Notepad*)
• `Close window` *(Alt+F4)*
• `Take a screenshot` / `Screenshot`
• `Find` *(Ctrl+F)*

🔊 **Media & Volume:**
• `Play <song> on YouTube` / `Play music`
• `Increase volume` / `Volume up` / `Louder`
• `Decrease volume` / `Volume down` / `Quieter`
• `Mute` / `Unmute`
• `Pause` / `Resume`
• `Next track` / `Previous track`

🔍 **Smart Search:**
• `Google <query>` or `Search Google for <topic>`
• `YouTube <query>` or `Search YouTube for <topic>`
• `Amazon <query>` or `Search Amazon for <product>`

📅 **Tasks, Calendar & Reminders:**
• `Add <task> to my list` / `Add to my todo list <task>`
• `Show my tasks` / `Get tasks` / `List tasks`
• `Remove <task> from my list`
• `Sort tasks` / `Show high priority tasks`
• `Calendar` / `Show upcoming events`
• `Remind me to <task> at <time>` (e.g. *Remind me to call mom at 5:00 pm*)

✍️ **Content & Productivity:**
• `Draft email for <topic>` / `Write email about <topic>` / `Email <topic>`
• `Write application for <topic>` / `Content <topic>`

⛅ **Live Telemetry & Info:**
• `Weather in <city>` / `What is the weather?`
• `What time is it?` / `What is the date?`

🧠 **General Intelligence (Google Gemini):**
• Ask any question, coding problem, explanation, translation, or conversation!"""
