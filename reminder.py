import time
from datetime import datetime, timedelta
import threading
from nova_alpha import setup_nova

def reminder(text):
    print(f"Input text: {text}")
    try:
        # Parse the command
        command = text.upper().replace("REMIND ME TO", "").strip()
        message, time_part = command.rsplit("AT", 1)
        message = message.strip()
        time_part = time_part.strip()

        # Normalize time (e.g., "p.m." -> "PM")
        time_part = time_part.replace(".", "").strip()

        # Determine time format
        if ":" in time_part and "AM" not in time_part and "PM" not in time_part:
            # Parse as 24-hour format
            alarm_time = datetime.strptime(time_part, "%H:%M").time()
        else:
            # Parse as 12-hour format (e.g., "5pm" -> "5:00 PM")
            if ":" not in time_part:
                time_part = time_part.replace("PM", ":00 PM").replace("AM", ":00 AM")
            alarm_time = datetime.strptime(time_part, "%I:%M %p").time()

        # Calculate reminder time
        now = datetime.now()
        reminder_time = datetime.combine(now.date(), alarm_time)
        if reminder_time < now:
            reminder_time += timedelta(days=1)  # Schedule for the next day if time has passed

        delay = (reminder_time - now).total_seconds()

        # Schedule the reminder
        threading.Timer(delay, trigger_reminder, args=[message]).start()
        print(f"Reminder set for {reminder_time.strftime('%I:%M %p')} (in {int(delay)} seconds): {message}")

    except ValueError as e:
        print(f"Error: {e}")
        print("Sorry, I couldn't understand the time format. Please use the format: 'remind me to [task] at [time]'.")

def trigger_reminder(message):
    print(f"Reminder: {message}")
    try:
        orion = setup_nova()
        orion.say(f"Reminder to {message}")
    except Exception as e:
        print(f"Error with nova setup or speech synthesis: {e}")

# Example usage
# reminder("remind me to call at 5:07 p.m.")  # Handles "p.m." format
