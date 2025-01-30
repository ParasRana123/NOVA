from nova_alpha import setup_nova, speak
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
import pickle
from datetime import datetime, timedelta

# Initialize Nova
global nova
nova = setup_nova()

# Google Calendar OAuth Scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Authenticate Google Calendar
def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Google Calendar Service
creds = authenticate_google_calendar()
calendar_service = build('calendar', 'v3', credentials=creds)

# To-Do List Functions
def read_list_from_file():
    try:
        with open('Tasks/todolist.txt', 'r') as file:
            todolist = file.readlines()
        return [task.strip() for task in todolist]
    except FileNotFoundError:
        return []

def write_list_to_file():
    with open('Tasks/todolist.txt', 'w') as file:
        for task in todolist:
            file.write(f"{task}\n")

todolist = read_list_from_file()

# Create Calendar Event Automatically for High Priority Tasks
import re

def extract_hour(task):
    match = re.search(r'(\d{1,2}):?(\d{2})?\s?(AM|PM)?', task, re.IGNORECASE)
    
    if not match:
        speak(nova, "Couldn't identify a valid time in the task description.")
        return None

    hour = int(match.group(1))
    minutes = int(match.group(2)) if match.group(2) else 0
    period = match.group(3).upper() if match.group(3) else None

    # Convert hour to 24-hour format
    if period == "PM" and hour != 12:
        hour += 12
    if period == "AM" and hour == 12:
        hour = 0

    return hour, minutes

def create_event(task):
    extracted_time = extract_hour(task)
    if not extracted_time:
        return
    
    h, m = extracted_time
    now = datetime.utcnow()
    event_start = datetime(now.year, now.month, now.day, h, m)
    event_end = event_start + timedelta(hours=0)  # Assuming a 1-hour event

    print(f"Event Start: {event_start}, Event End: {event_end}")

    event = {
        'summary': task,
        'start': {'dateTime': event_start.isoformat() + 'Z', 'timeZone': 'UTC'},
        'end': {'dateTime': event_end.isoformat() + 'Z', 'timeZone': 'UTC'},
        'reminders': {
            'useDefault': False,
            'overrides': [{'method': 'popup', 'minutes': 10}],
        },
    }

    event = calendar_service.events().insert(calendarId='primary', body=event).execute()
    speak(nova, f"'{task}' added to your Google Calendar.")

# Add Task
def add_task(text):
    global todolist
    todolist.append(text)
    speak(nova, f"Added '{text}' to your to-do list.")
    write_list_to_file()

    # Automatically add high-priority tasks to Google Calendar
    # if "high" in text.lower():
    create_event(text)

# Remove Task
def remove_task(text):
    global todolist
    if text in todolist:
        todolist.remove(text)
        speak(nova, f"Removed '{text}' from your to-do list.")
        write_list_to_file()
    else:
        speak(nova, f"'{text}' not found in the to-do list.")

# Get Tasks
def get_tasks():
    global todolist
    if todolist:
        speak(nova, "Here is your to-do list:")
        for task in todolist:
            speak(nova, task)
    else:
        speak(nova, "Your to-do list is empty.")

# Sort Tasks
def sort_tasks():
    global todolist
    high_priority, med_priority, low_priority = [], [], []

    for task in todolist:
        if "high" in task.lower():
            high_priority.append(task)
        elif "med" in task.lower():
            med_priority.append(task)
        elif "low" in task.lower():
            low_priority.append(task)

    with open('Tasks/high_priority.txt', 'w') as file:
        for task in high_priority:
            file.write(f"{task}\n")

    with open('Tasks/med_priority.txt', 'w') as file:
        for task in med_priority:
            file.write(f"{task}\n")

    with open('Tasks/low_priority.txt', 'w') as file:
        for task in low_priority:
            file.write(f"{task}\n")

    speak(nova, "Tasks have been sorted into high, medium, and low priority files.")

# Search Tasks
def search_tasks(keyword):
    results = [task for task in todolist if keyword.lower() in task.lower()]
    if results:
        speak(nova, f"Tasks matching '{keyword}':")
        for task in results:
            speak(nova, task)
    else:
        speak(nova, f"No tasks matching '{keyword}' found.")

# Get Tasks by Priority
def get_tasks_by_priority(priority):
    try:
        with open(f'Tasks/{priority}_priority.txt', 'r') as file:
            tasks = file.readlines()
        if tasks:
            speak(nova, f"Here are your {priority} priority tasks:")
            for task in tasks:
                speak(nova, task.strip())
        else:
            speak(nova, f"No {priority} priority tasks found.")
    except FileNotFoundError:
        speak(nova, f"No {priority} priority tasks file found.")

# Get Upcoming Events
def get_upcoming_events():
    now = datetime.utcnow().isoformat() + 'Z'
    events_result = calendar_service.events().list(
        calendarId='primary', timeMin=now, maxResults=10,
        singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak(nova, "No upcoming events found.")
        return

    speak(nova, "Here are your upcoming events:")
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        speak(nova, f"{event['summary']} at {start}")

# Main Function 
def todomain(command):
    if "add" in command:
        task = command.split("add ")[1].strip()
        add_task(task)
    elif "remove" in command:
        task = command.split("remove ")[1].strip()
        remove_task(task)
    elif "get" in command:
        get_tasks()
    elif "sort" in command:
        sort_tasks()
    elif "search" in command:
        keyword = command.split("search ")[1].strip()
        search_tasks(keyword)
    elif "priority" in command:
        priority = command.split("priority ")[1].strip()
        get_tasks_by_priority(priority)
    elif "calendar" in command:
        get_upcoming_events()
    else:
        speak(nova, "Invalid command. Please try again.")
# todomain("add in my list to call mom at 2pm")

