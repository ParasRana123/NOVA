import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
except ImportError:
    InstalledAppFlow, build, Request = None, None, None

from backend.config import TOKEN_PICKLE_PATH, CREDENTIALS_PATH, CALENDAR_SCOPES

class CalendarService:
    def __init__(self):
        self.service = None
        self._init_service()

    def _init_service(self):
        if not build:
            return
        try:
            creds = None
            if os.path.exists(TOKEN_PICKLE_PATH):
                with open(TOKEN_PICKLE_PATH, 'rb') as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token and Request:
                    creds.refresh(Request())
                elif os.path.exists(CREDENTIALS_PATH) and InstalledAppFlow:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(CREDENTIALS_PATH), CALENDAR_SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    with open(TOKEN_PICKLE_PATH, 'wb') as token:
                        pickle.dump(creds, token)

            if creds and creds.valid:
                self.service = build('calendar', 'v3', credentials=creds)
        except Exception as e:
            print(f"[CalendarService] Calendar auth info/warning: {e}")
            self.service = None

    def is_authenticated(self) -> bool:
        return self.service is not None

    def get_upcoming_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Fetch list of upcoming events from Google Calendar."""
        if not self.service:
            return []
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            return events_result.get('items', [])
        except Exception as e:
            print(f"[CalendarService] Error fetching events: {e}")
            return []

    def create_event(
        self,
        summary: str,
        start_datetime: datetime,
        duration_hours: int = 1,
        reminder_minutes: int = 10
    ) -> Optional[Dict[str, Any]]:
        """Create a new event on Google Calendar."""
        if not self.service:
            print("[CalendarService] Cannot create event: Calendar not authenticated.")
            return None
        try:
            end_datetime = start_datetime + timedelta(hours=duration_hours)
            event_body = {
                'summary': summary,
                'start': {'dateTime': start_datetime.isoformat() + 'Z', 'timeZone': 'UTC'},
                'end': {'dateTime': end_datetime.isoformat() + 'Z', 'timeZone': 'UTC'},
                'reminders': {
                    'useDefault': False,
                    'overrides': [{'method': 'popup', 'minutes': reminder_minutes}],
                },
            }
            created_event = self.service.events().insert(
                calendarId='primary', body=event_body
            ).execute()
            return created_event
        except Exception as e:
            print(f"[CalendarService] Error creating event: {e}")
            return None

default_calendar_service = CalendarService()
