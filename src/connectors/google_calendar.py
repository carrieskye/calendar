import os
import time
from datetime import datetime, date
from datetime import time as datetime_time
from typing import List, Dict

from dateutil.relativedelta import relativedelta
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
# noinspection PyPackageRequirements
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.models.calendar import Calendar, Owner
from src.models.event import Event
from src.utils.file import File
from src.utils.formatter import Formatter
from src.utils.logger import Logger

Logger.title('Loading connectors')


def load_credentials(scopes: List[str]) -> Credentials:
    credentials = None
    if os.path.exists('src/credentials/token.pickle'):
        credentials = File.read_pickle('src/credentials/token.pickle')

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('src/credentials/credentials.json', scopes)
            credentials = flow.run_local_server(port=0)
        File.write_pickle(credentials, 'src/credentials/token.pickle')

    return credentials


class GoogleCalAPI:
    Logger.sub_sub_title('Loading Google Calendar')
    scopes = ['https://www.googleapis.com/auth/calendar']
    service = build('calendar', 'v3', credentials=load_credentials(scopes))

    @classmethod
    def get_calendars(cls) -> Dict[str, str]:
        ignore = ['Hayley', 'Trakt', 'Todoist', 'Contacts', 'peelmancarolyne@gmail.com', 'Larry',
                  'Holidays in United Kingdom', 'Wina', 'lb@deliowealth.com']
        calendar_list = cls.service.calendarList().list().execute().get('items', [])
        calendar_list = {Formatter.normalise(calendar.get('summaryOverride')) if calendar.get('summaryOverride')
                         else Formatter.normalise(calendar.get('summary')): calendar.get('id')
                         for calendar in calendar_list if calendar.get('summary') not in ignore}
        sorted_calendars = sorted(calendar_list.items(), key=lambda x: x[0])
        return {calendar[0]: calendar[1] for calendar in sorted_calendars}

    @classmethod
    def get_events(cls, calendar: Calendar, owner: Owner, max_results: int, time_min: datetime,
                   time_max: datetime = datetime.now()) -> List[Event]:
        try:
            events = cls.service.events().list(
                calendarId=calendar.get_cal_id(owner),
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute().get('items', [])
            return [Event.from_dict(event, calendar, owner) for event in events]
        except HttpError:
            Logger.log('Rate limit exceeded, trying again in 90s.')
            time.sleep(90)
            return cls.get_events(calendar, owner, max_results, time_min, time_max)

    @classmethod
    def get_all_events_for_day(cls, start: date):
        from src.data.data import Data

        start = datetime.combine(start, datetime_time(4, 0))
        end = start + relativedelta(days=1)

        return [event for calendar_name, calendar in Data.calendar_dict.items()
                for owner, cal_id in calendar.get_calendars().items()
                for event in cls.get_events(calendar, owner, 100, start, end)]

    @classmethod
    def delete_event(cls, calendar_id: str, event_id: str):
        try:
            return cls.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
        except HttpError:
            Logger.log('Rate limit exceeded, trying again in 90s.')
            time.sleep(90)
            return cls.delete_event(calendar_id, event_id)

    @classmethod
    def create_event(cls, calendar_id: str, event: Event):
        try:
            return cls.service.events().insert(
                calendarId=calendar_id,
                body=event.serialise_for_google()
            ).execute()
        except HttpError:
            Logger.log('Rate limit exceeded, trying again in 90s.')
            time.sleep(90)
            return cls.create_event(calendar_id, event)

    @classmethod
    def update_event(cls, calendar_id: str, event_id: str, event: Event):
        try:
            return cls.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event.serialise_for_google()
            ).execute()
        except HttpError:
            Logger.log('Rate limit exceeded, trying again in 90s.')
            time.sleep(90)
            return cls.update_event(calendar_id, event_id, event)

    @classmethod
    def move_event(cls, calendar_id: str, event_id: str, destination: str):
        try:
            return cls.service.events().move(
                calendarId=calendar_id,
                eventId=event_id,
                destination=destination
            ).execute()
        except HttpError:
            Logger.log('Rate limit exceeded, trying again in 90s.')
            time.sleep(90)
            return cls.move_event(calendar_id, event_id, destination)

    @classmethod
    def get_event_instances(cls, calendar_id: str, event_id: str):
        try:
            return cls.service.events().instances(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
        except HttpError:
            Logger.log('Rate limit exceeded, trying again in 90s.')
            time.sleep(90)
            return cls.get_event_instances(calendar_id, event_id)
