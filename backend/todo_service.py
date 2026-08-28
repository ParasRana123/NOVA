import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple
from backend.config import TASKS_DIR
from backend.speech_service import speak
from backend.calendar_service import default_calendar_service

TODOLIST_PATH = TASKS_DIR / "todolist.txt"
HIGH_PRIORITY_PATH = TASKS_DIR / "high_priority.txt"
MED_PRIORITY_PATH = TASKS_DIR / "med_priority.txt"
LOW_PRIORITY_PATH = TASKS_DIR / "low_priority.txt"

def read_tasks_from_file(file_path: Path = TODOLIST_PATH) -> List[str]:
    """Read lines from a tasks file."""
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return [task.strip() for task in file.readlines() if task.strip()]
        except IOError:
            return []
    return []

def write_tasks_to_file(tasks: List[str], file_path: Path = TODOLIST_PATH):
    """Write list of tasks to file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for task in tasks:
                file.write(f"{task}\n")
    except IOError as e:
        print(f"[TodoService] Error writing tasks: {e}")

def extract_hour(task: str) -> Optional[Tuple[int, int]]:
    """Extract hour and minutes from natural language task description."""
    match = re.search(r'(\d{1,2}):?(\d{2})?\s*(AM|PM)?', task, re.IGNORECASE)
    if not match:
        return None

    hour = int(match.group(1))
    minutes = int(match.group(2)) if match.group(2) else 0
    period = match.group(3).upper() if match.group(3) else None

    # Convert to 24-hour format
    if period == "PM" and hour != 12:
        hour += 12
    elif period == "AM" and hour == 12:
        hour = 0

    return hour, minutes

def create_calendar_event_for_task(task: str):
    """Attempt to create a Google Calendar event for the task if a time is specified."""
    time_tuple = extract_hour(task)
    if not time_tuple:
        return

    h, m = time_tuple
    now = datetime.utcnow()
    event_start = datetime(now.year, now.month, now.day, h, m)
    
    res = default_calendar_service.create_event(summary=task, start_datetime=event_start)
    if res:
        speak(f"'{task}' added to your Google Calendar.")

def add_task(text: str):
    """Add a new task to to-do list and sync with calendar."""
    clean_task = text.strip()
    if not clean_task:
        speak("Task description cannot be empty.")
        return

    tasks = read_tasks_from_file()
    tasks.append(clean_task)
    write_tasks_to_file(tasks)
    speak(f"Added '{clean_task}' to your to-do list.")
    create_calendar_event_for_task(clean_task)

def remove_task(text: str):
    """Remove an existing task from to-do list."""
    clean_task = text.strip()
    tasks = read_tasks_from_file()
    
    # Try exact match or substring match
    matched = [t for t in tasks if clean_task.lower() in t.lower()]
    if matched:
        for m in matched:
            tasks.remove(m)
            speak(f"Removed '{m}' from your to-do list.")
        write_tasks_to_file(tasks)
    else:
        speak(f"'{clean_task}' not found in the to-do list.")

def get_tasks():
    """Speak all tasks in the to-do list."""
    tasks = read_tasks_from_file()
    if tasks:
        speak("Here is your to-do list:")
        for task in tasks:
            speak(task)
    else:
        speak("Your to-do list is empty.")

def sort_tasks():
    """Categorize tasks into high, medium, and low priority files."""
    tasks = read_tasks_from_file()
    high, med, low = [], [], []

    for task in tasks:
        t_low = task.lower()
        if "high" in t_low:
            high.append(task)
        elif "med" in t_low or "medium" in t_low:
            med.append(task)
        elif "low" in t_low:
            low.append(task)
        else:
            med.append(task)

    write_tasks_to_file(high, HIGH_PRIORITY_PATH)
    write_tasks_to_file(med, MED_PRIORITY_PATH)
    write_tasks_to_file(low, LOW_PRIORITY_PATH)
    speak("Tasks have been sorted into high, medium, and low priority lists.")

def search_tasks(keyword: str):
    """Search tasks by keyword."""
    tasks = read_tasks_from_file()
    results = [t for t in tasks if keyword.lower() in t.lower()]
    if results:
        speak(f"Found {len(results)} task(s) matching '{keyword}':")
        for task in results:
            speak(task)
    else:
        speak(f"No tasks matching '{keyword}' were found.")

def get_tasks_by_priority(priority: str):
    """Fetch tasks from priority files."""
    p = priority.lower().strip()
    file_map = {
        "high": HIGH_PRIORITY_PATH,
        "med": MED_PRIORITY_PATH,
        "medium": MED_PRIORITY_PATH,
        "low": LOW_PRIORITY_PATH
    }
    target_file = file_map.get(p, MED_PRIORITY_PATH)
    tasks = read_tasks_from_file(target_file)
    if tasks:
        speak(f"Here are your {priority} priority tasks:")
        for task in tasks:
            speak(task)
    else:
        speak(f"No {priority} priority tasks found.")

def get_upcoming_calendar_events():
    """Fetch and speak upcoming events from Google Calendar."""
    events = default_calendar_service.get_upcoming_events()
    if not events:
        speak("No upcoming calendar events found.")
        return

    speak("Here are your upcoming events:")
    for event in events:
        start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', ''))
        summary = event.get('summary', 'Untitled Event')
        speak(f"{summary} at {start}")

def handle_todo_command(command: str):
    """Main routing function for to-do & calendar operations."""
    cmd = command.lower()
    if "add" in cmd:
        task = command.split("add", 1)[1].replace("in my list", "").replace("to my list", "").strip()
        add_task(task)
    elif "remove" in cmd:
        task = command.split("remove", 1)[1].replace("from my list", "").strip()
        remove_task(task)
    elif "get" in cmd or "show" in cmd or "list" in cmd:
        get_tasks()
    elif "sort" in cmd:
        sort_tasks()
    elif "search" in cmd:
        keyword = command.split("search", 1)[1].strip()
        search_tasks(keyword)
    elif "priority" in cmd:
        priority = command.split("priority", 1)[1].strip()
        get_tasks_by_priority(priority)
    elif "calendar" in cmd or "events" in cmd:
        get_upcoming_calendar_events()
    else:
        speak("Invalid task command. Please try again.")

# Alias for backwards compatibility
todomain = handle_todo_command
