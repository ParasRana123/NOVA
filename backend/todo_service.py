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
    match = re.search(r'\b(\d{1,2})(?::(\d{2}))?\s*(AM|PM)?\b', task, re.IGNORECASE)
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

def create_calendar_event_for_task(task: str) -> Optional[str]:
    """Attempt to create a Google Calendar event for the task if a time is specified."""
    time_tuple = extract_hour(task)
    if not time_tuple:
        return None

    h, m = time_tuple
    now = datetime.utcnow()
    event_start = datetime(now.year, now.month, now.day, h, m)
    
    res = default_calendar_service.create_event(summary=task, start_datetime=event_start)
    if res:
        msg = f"'{task}' added to your Google Calendar."
        speak(msg)
        return msg
    return None

def add_task(text: str) -> str:
    """Add a new task to to-do list and sync with calendar."""
    clean_task = text.strip()
    if not clean_task:
        msg = "Task description cannot be empty."
        speak(msg)
        return msg

    tasks = read_tasks_from_file()
    tasks.append(clean_task)
    write_tasks_to_file(tasks)
    msg = f"Added '{clean_task}' to your to-do list."
    speak(msg)
    cal_msg = create_calendar_event_for_task(clean_task)
    if cal_msg:
        msg += f" ({cal_msg})"
    return msg

def remove_task(text: str) -> str:
    """Remove an existing task from to-do list."""
    clean_task = text.strip()
    tasks = read_tasks_from_file()
    
    matched = [t for t in tasks if clean_task.lower() in t.lower()]
    if matched:
        for m in matched:
            tasks.remove(m)
        write_tasks_to_file(tasks)
        msg = f"Removed '{matched[0]}' from your to-do list."
        speak(msg)
        return msg
    else:
        msg = f"'{clean_task}' not found in the to-do list."
        speak(msg)
        return msg

def get_tasks() -> str:
    """Return and speak all tasks in the to-do list."""
    tasks = read_tasks_from_file()
    if tasks:
        formatted = "\n".join([f"{i+1}. {t}" for i, t in enumerate(tasks)])
        msg = f"Here is your to-do list:\n{formatted}"
        speak(f"You have {len(tasks)} tasks in your to-do list.")
        return msg
    else:
        msg = "Your to-do list is currently empty."
        speak(msg)
        return msg

def sort_tasks() -> str:
    """Categorize tasks into high, medium, and low priority files."""
    tasks = read_tasks_from_file()
    high, med, low = [], [], []

    for task in tasks:
        t_low = task.lower()
        if "high" in t_low:
            high.append(task)
        elif "low" in t_low:
            low.append(task)
        else:
            med.append(task)

    write_tasks_to_file(high, HIGH_PRIORITY_PATH)
    write_tasks_to_file(med, MED_PRIORITY_PATH)
    write_tasks_to_file(low, LOW_PRIORITY_PATH)
    msg = f"Tasks sorted into {len(high)} high, {len(med)} medium, and {len(low)} low priority lists."
    speak(msg)
    return msg

def search_tasks(keyword: str) -> str:
    """Search tasks by keyword."""
    tasks = read_tasks_from_file()
    results = [t for t in tasks if keyword.lower() in t.lower()]
    if results:
        formatted = "\n".join([f"- {t}" for t in results])
        msg = f"Found {len(results)} task(s) matching '{keyword}':\n{formatted}"
        speak(f"Found {len(results)} matching tasks.")
        return msg
    else:
        msg = f"No tasks matching '{keyword}' were found."
        speak(msg)
        return msg

def get_tasks_by_priority(priority: str) -> str:
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
        formatted = "\n".join([f"{i+1}. {t}" for i, t in enumerate(tasks)])
        msg = f"Here are your {priority} priority tasks:\n{formatted}"
        speak(f"Here are your {priority} priority tasks.")
        return msg
    else:
        msg = f"No {priority} priority tasks found."
        speak(msg)
        return msg

def get_upcoming_calendar_events() -> str:
    """Fetch and speak upcoming events from Google Calendar."""
    events = default_calendar_service.get_upcoming_events()
    if not events:
        msg = "No upcoming calendar events found."
        speak(msg)
        return msg

    formatted_events = []
    for event in events:
        start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', ''))
        summary = event.get('summary', 'Untitled Event')
        formatted_events.append(f"• {summary} at {start}")

    msg = "Upcoming Google Calendar Events:\n" + "\n".join(formatted_events)
    speak(f"You have {len(events)} upcoming calendar events.")
    return msg

def handle_todo_command(command: str) -> Optional[str]:
    """Strict matching function for to-do & calendar operations."""
    cmd = command.lower().strip()

    # Add task
    add_match = re.search(r'^(?:add\s+to\s+(?:my\s+)?(?:todo|to-do|tasks?)(?:\s+list)?|add\s+(?:task|in\s+my\s+list)\s+)(.+)$', cmd)
    if not add_match:
        add_match = re.search(r'^add\s+(.+?)\s+to\s+(?:my\s+)?(?:todo|to-do|tasks?|list|todo\s+list|to-do\s+list)$', cmd)
    if add_match:
        return add_task(add_match.group(1).strip())

    # Remove task
    remove_match = re.search(r'^(?:remove|delete)\s+(.+?)\s+from\s+(?:my\s+)?(?:todo|to-do|tasks?|list|todo\s+list|to-do\s+list)$', cmd)
    if not remove_match:
        remove_match = re.search(r'^(?:remove|delete)\s+task\s+(.+)$', cmd)
    if remove_match:
        return remove_task(remove_match.group(1).strip())

    # Show tasks
    if re.search(r'^(?:show|get|view|read|list)\s+(?:my\s+)?(?:todo|to-do|tasks?)(?:\s+list)?$', cmd):
        return get_tasks()

    # Sort tasks
    if re.search(r'^sort\s+(?:my\s+)?(?:tasks?|todo|to-do)(?:\s+list)?$', cmd):
        return sort_tasks()

    # Search tasks
    search_match = re.search(r'^search\s+(?:tasks?|todo)\s+for\s+(.+)$', cmd)
    if search_match:
        return search_tasks(search_match.group(1).strip())

    # Priority tasks
    priority_match = re.search(r'^(?:show|get)\s+(high|med|medium|low)\s+priority\s+tasks?$', cmd)
    if priority_match:
        return get_tasks_by_priority(priority_match.group(1))

    # Calendar events
    if re.search(r'^(?:show|get|view)\s+(?:my\s+)?(?:calendar|upcoming\s+events?)$', cmd):
        return get_upcoming_calendar_events()

    return None

todomain = handle_todo_command
