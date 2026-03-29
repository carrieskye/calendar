import logging
import time
from datetime import date, datetime, time as datetime_time
from pathlib import Path

from dateutil.relativedelta import relativedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.enums import Owner
from src.models.calendar import Calendar
from src.models.event import Event
from src.utils import Formatter

logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
logger.info(Formatter.title("Loading connectors"))


def load_credentials(scopes: list[str]) -> Credentials:
    credentials = None
    token_file = Path("src/credentials/token.json")
    if token_file.exists():
        credentials = Credentials.from_authorized_user_file(str(token_file), scopes)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("src/credentials/credentials.json", scopes)
            credentials = flow.run_local_server(port=0)
        with open(token_file, "w", encoding="utf-8") as f:
            f.write(credentials.to_json())

    return credentials


class GoogleCalAPI:
    logger.info("Loading Google Calendar")
    scopes = ["https://www.googleapis.com/auth/calendar"]
    service = build("calendar", "v3", credentials=load_credentials(scopes))

    @classmethod
    def get_calendars(cls) -> dict[str, str]:
        ignore = [
            "Trakt",
            "Todoist",
            "Contacts",
            "user@example.com",
            "Partner",
            "Birthdays",
            "Holidays in United Kingdom",
            "contact1@example.com",
            "user.work@example.com",
            "user.vc@example.com",
            "Shared Contact",
            "Contact Shared",
        ]
        raw_items = cls.service.calendarList().list().execute().get("items", [])
        calendar_list: dict[str, str] = {}
        for calendar in raw_items:
            if calendar.get("summary") in ignore:
                continue
            key = (
                Formatter.normalise(calendar.get("summaryOverride"))
                if calendar.get("summaryOverride")
                else Formatter.normalise(calendar.get("summary"))
            )
            calendar_list[key] = calendar.get("id")
        sorted_calendars = sorted(calendar_list.items(), key=lambda x: x[0])
        return {calendar[0]: calendar[1] for calendar in sorted_calendars}

    @classmethod
    def get_events(
        cls,
        calendar: Calendar,
        owner: Owner,
        max_results: int,
        time_min: datetime,
        time_max: datetime,
    ) -> list[Event]:
        try:
            events = (
                cls.service.events()
                .list(
                    calendarId=calendar.get_cal_id(owner),
                    timeMin=time_min.isoformat() + "Z",
                    timeMax=time_max.isoformat() + "Z",
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
                .get("items", [])
            )
            return [Event.from_dict(event, calendar, owner) for event in events]
        except HttpError as e:
            if e.reason == "Rate Limit Exceeded":
                logger.error("Rate limit exceeded, trying again in 30s.")
                time.sleep(30)
                return cls.get_events(calendar, owner, max_results, time_min, time_max)
            raise e

    @classmethod
    def get_all_events_for_day(cls, start: date) -> list[Event]:
        from src.data import Data

        start = datetime.combine(start, datetime_time(4))
        end = start + relativedelta(days=1)

        return [
            event
            for calendar_name, calendar in Data.calendar_dict.items()
            for owner, cal_id in calendar.get_calendars().items()
            for event in cls.get_events(calendar, owner, 100, start, end)
        ]

    @classmethod
    def delete_event(cls, calendar_id: str, event_id: str) -> None:
        try:
            return cls.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        except HttpError as e:
            if e.reason == "Rate Limit Exceeded":
                logger.error("Rate limit exceeded, trying again in 30s.")
                time.sleep(30)
                return cls.delete_event(calendar_id, event_id)
            raise e

    @classmethod
    def create_event(cls, calendar_id: str, event: Event) -> Event:
        try:
            return cls.service.events().insert(calendarId=calendar_id, body=event.serialise_for_google()).execute()
        except HttpError as e:
            if e.reason == "Rate Limit Exceeded":
                logger.error("Rate limit exceeded, trying again in 30s.")
                time.sleep(30)
                return cls.create_event(calendar_id, event)
            raise e

    @classmethod
    def update_event(cls, calendar_id: str, event_id: str, event: Event) -> Event:
        try:
            return (
                cls.service.events()
                .update(
                    calendarId=calendar_id,
                    eventId=event_id,
                    body=event.serialise_for_google(),
                )
                .execute()
            )
        except HttpError as e:
            if e.reason == "Rate Limit Exceeded":
                logger.error("Rate limit exceeded, trying again in 30s.")
                time.sleep(30)
                return cls.update_event(calendar_id, event_id, event)
            raise e

    @classmethod
    def move_event(cls, calendar_id: str, event_id: str, destination: str) -> Event:
        try:
            return (
                cls.service.events().move(calendarId=calendar_id, eventId=event_id, destination=destination).execute()
            )
        except HttpError as e:
            if e.reason == "Rate Limit Exceeded":
                logger.error("Rate limit exceeded, trying again in 30s.")
                time.sleep(30)
                return cls.move_event(calendar_id, event_id, destination)
            raise e

    @classmethod
    def get_event_instances(cls, calendar_id: str, event_id: str) -> list[Event]:
        try:
            return cls.service.events().instances(calendarId=calendar_id, eventId=event_id).execute()
        except HttpError as e:
            if e.reason == "Rate Limit Exceeded":
                logger.error("Rate limit exceeded, trying again in 30s.")
                time.sleep(30)
                return cls.get_event_instances(calendar_id, event_id)
            raise e
