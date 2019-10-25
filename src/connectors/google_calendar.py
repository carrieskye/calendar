import os
import pickle
from datetime import datetime

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.models.event import Event

SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarAPI:

    def __init__(self):
        credentials = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                credentials = pickle.load(token)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                credentials = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(credentials, token)

        self.service = build('calendar', 'v3', credentials=credentials)

    def get_calendars(self):
        return self.service.calendarList().list().execute().get('items', [])

    def get_calendar_id(self, calendar_name: str):
        calendars = self.get_calendars()
        for calendar in calendars:
            if calendar.get('summary').lower() == calendar_name:
                return calendar.get('id')

    def get_events(self, calendar_id: str, time_min: datetime, max_results: int):
        return self.service.events().list(
            calendarId=calendar_id,
            timeMin=time_min.isoformat() + 'Z',
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])

    def create_event(self, calendar_id: str, event: Event):
        return self.service.events().insert(
            calendarId=calendar_id,
            body=event.to_dict()
        ).execute()

    def update_event(self, calendar_id: str, event_id: str, event: Event):
        return self.service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event.to_dict()
        )
