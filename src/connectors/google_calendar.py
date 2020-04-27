import os
from datetime import datetime, time, date
from typing import List, Dict

from dateutil.relativedelta import relativedelta
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
# noinspection PyPackageRequirements
from googleapiclient.discovery import build

from src.models.calendar import Calendar, Owner
from src.models.event import Event
from src.utils.utils import Utils


def load_credentials(scopes: List[str]) -> Credentials:
    credentials = None
    if os.path.exists('src/credentials/token.pickle'):
        credentials = Utils.read_pickle('src/credentials/token.pickle')

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('src/credentials/credentials.json', scopes)
            credentials = flow.run_local_server(port=0)
        Utils.write_pickle(credentials, 'src/credentials/token.pickle')

    return credentials


class GoogleCalAPI:
    scopes = ['https://www.googleapis.com/auth/calendar']
    service = build('calendar', 'v3', credentials=load_credentials(scopes))

    @classmethod
    def get_calendars(cls) -> Dict[str, str]:
        ignore = ['Baby', 'Trakt', 'Todoist', 'Contacts', 'peelmancarolyne@gmail.com', 'Larry',
                  'Holidays in United Kingdom', 'Wina']
        calendar_list = cls.service.calendarList().list().execute().get('items', [])
        calendar_list = {Utils.normalise(calendar.get('summaryOverride')) if calendar.get('summaryOverride')
                         else Utils.normalise(calendar.get('summary')): calendar.get('id')
                         for calendar in calendar_list if calendar.get('summary') not in ignore}
        sorted_calendars = sorted(calendar_list.items(), key=lambda x: x[0])
        return {calendar[0]: calendar[1] for calendar in sorted_calendars}

    @classmethod
    def get_events(cls, calendar: Calendar, owner: Owner, max_results: int, time_min: datetime,
                   time_max: datetime = datetime.now()) -> List[Event]:
        events = cls.service.events().list(
            calendarId=calendar.get_cal_id(owner),
            timeMin=time_min.isoformat() + 'Z',
            timeMax=time_max.isoformat() + 'Z',
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])
        return [Event.from_dict(event, calendar, owner) for event in events]

    @classmethod
    def get_all_events_for_day(cls, start: date):
        from src.data.data import Data

        start = datetime.combine(start, time(4, 0))
        end = start + relativedelta(days=1)

        return [event for calendar_name, calendar in Data.calendar_dict.items()
                for owner, cal_id in calendar.get_calendars().items()
                for event in cls.get_events(calendar, owner, 100, start, end)]

    @classmethod
    def delete_event(cls, calendar_id: str, event_id: str):
        return cls.service.events().delete(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()

    @classmethod
    def create_event(cls, calendar_id: str, event: Event):
        return cls.service.events().insert(
            calendarId=calendar_id,
            body=event.serialise_for_google()
        ).execute()

    @classmethod
    def update_event(cls, calendar_id: str, event_id: str, event: Event):
        return cls.service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event.serialise_for_google()
        ).execute()

    @classmethod
    def move_event(cls, calendar_id: str, event_id: str, destination: str):
        return cls.service.events().move(
            calendarId=calendar_id,
            eventId=event_id,
            destination=destination
        ).execute()

    @classmethod
    def get_event_instances(cls, calendar_id: str, event_id: str):
        response = cls.service.events().instances(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        return response
