import os
import pickle
from datetime import datetime

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.models.event import Event
from src.utils.utils import Utils

SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarAPI:

    def __init__(self):
        credentials = None
        if os.path.exists('src/credentials/token.pickle'):
            with open('src/credentials/token.pickle', 'rb') as token:
                credentials = pickle.load(token)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('src/credentials/credentials.json', SCOPES)
                credentials = flow.run_local_server(port=0)
            with open('src/credentials/token.pickle', 'wb') as token:
                pickle.dump(credentials, token)

        self.service = build('calendar', 'v3', credentials=credentials)
        self.calendars = Utils.read_json('data/google/calendars.json')

    def update_calendar_dict(self):
        ignore = ['Trakt', 'Todoist', 'Contacts', 'peelmancarolyne@gmail.com', 'Larry']
        calendar_list = self.service.calendarList().list().execute().get('items', [])
        calendar_list = {Utils.normalise(calendar.get('summaryOverride')) if calendar.get('summaryOverride')
                         else Utils.normalise(calendar.get('summary')): calendar.get('id')
                         for calendar in calendar_list if calendar.get('summary') not in ignore}
        sorted_calendars = sorted(calendar_list.items(), key=lambda x: x[0])
        sorted_calendar_dict = {calendar[0]: calendar[1] for calendar in sorted_calendars}
        Utils.write_json(sorted_calendar_dict, 'data/google/calendars.json')

    def get_calendar_id(self, calendar_name: str):
        return self.calendars[calendar_name]

    def get_events(self, calendar_id: str, max_results: int, time_min: datetime, time_max: datetime = datetime.now()):
        return self.service.events().list(
            calendarId=calendar_id,
            timeMin=time_min.isoformat() + 'Z',
            timeMax=time_max.isoformat() + 'Z',
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])

    def delete_event(self, calendar_id: str, event_id: str):
        return self.service.events().delete(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()

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
        ).execute()

    def move_event(self, calendar_id: str, event_id: str, destination: str):
        return self.service.events().move(
            calendarId=calendar_id,
            eventId=event_id,
            destination=destination
        ).execute()

    def get_event_instances(self, calendar_id: str, event_id: str):
        response = self.service.events().instances(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        return response

    def get_calendars_from_string(self, calendars: str):
        if calendars == 'all':
            return self.calendars
        else:
            return {calendar_name: calendar_id
                    for calendar_name, calendar_id in self.calendars.items()
                    if calendar_name in calendars.split(',')}
