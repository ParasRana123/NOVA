import re
import threading
from datetime import datetime, timedelta
from typing import Optional, Tuple
from backend.speech_service import speak

def parse_time_str(time_part: str) -> Optional[datetime]:
    """Parse time strings like '5pm', '5:30 PM', '17:00' into a datetime object for today/tomorrow."""
    try:
        clean_time = time_part.upper().replace(".", "").strip()
        now = datetime.now()

        # Handle 24-hour format (e.g. 14:30)
        if ":" in clean_time and "AM" not in clean_time and "PM" not in clean_time:
            parsed_time = datetime.strptime(clean_time, "%H:%M").time()
        else:
            # Handle 12-hour format (e.g. 5pm -> 5:00 PM)
            if ":" not in clean_time:
                clean_time = clean_time.replace("PM", ":00 PM").replace("AM", ":00 AM")
            parsed_time = datetime.strptime(clean_time, "%I:%M %p").time()

        reminder_dt = datetime.combine(now.date(), parsed_time)
        if reminder_dt < now:
            reminder_dt += timedelta(days=1)  # Rollover to tomorrow if time has passed
        return reminder_dt
    except Exception as e:
        print(f"[ReminderService] Error parsing time '{time_part}': {e}")
        return None

def trigger_reminder(message: str):
    """Callback function when reminder timer fires."""
    print(f"[Reminder Triggered]: {message}")
    speak(f"Sir, here is your reminder: {message}")

def reminder(text: str) -> Tuple[bool, str]:
    """
    Parse a natural-language reminder command and schedule a background timer.
    Example: 'remind me to call mom at 5:00 pm'
    Returns: (success: bool, status_message: str)
    """
    match = re.search(r'^(?:remind\s+me\s+(?:to\s+)?|set\s+(?:a\s+)?reminder\s+(?:to\s+)?)(.+?)\s+at\s+([0-9:apm\.\s]+)$', text.strip(), re.IGNORECASE)
    if not match:
        return False, "Not a valid reminder command format."

    message = match.group(1).strip()
    time_part = match.group(2).strip()

    reminder_dt = parse_time_str(time_part)
    if not reminder_dt:
        msg = f"Couldn't parse time '{time_part}'. Please use formats like '5 PM' or '14:30'."
        speak(msg)
        return False, msg

    now = datetime.now()
    delay_seconds = (reminder_dt - now).total_seconds()

    # Schedule timer
    timer = threading.Timer(delay_seconds, trigger_reminder, args=[message])
    timer.daemon = True
    timer.start()

    formatted_time = reminder_dt.strftime('%I:%M %p')
    msg = f"Reminder set for {formatted_time} to {message}"
    speak(msg)
    return True, msg
