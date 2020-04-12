from __future__ import annotations

from src.models.event_datetime import EventDateTime
from src.utils.utils import Utils


class Event:

    def __init__(self, summary: str, location: str, start: EventDateTime, end: EventDateTime, description: str = '',
                 event_id: str = '', calendar: str = '', calendar_id: str = ''):
        self.summary = summary
        self.location = location if location else ''
        self.description = description if description else ''
        self.start = start
        self.end = end
        self.event_id = event_id
        self.calendar = calendar
        self.calendar_id = calendar_id

    def __dict__(self) -> dict:
        return {
            'summary': self.summary,
            'location': self.location,
            'description': self.description,
            'start': self.start.to_dict(),
            'end': self.end.to_dict(),
            'visibility': 'default'
        }

    @staticmethod
    def get_event(original: dict, calendar_id: str, calendar: str = '') -> Event:
        return Event(
            summary=original.get('summary'),
            location=original.get('location'),
            description=original.get('description'),
            start=EventDateTime.get_event_date_time(original.get('start')),
            end=EventDateTime.get_event_date_time(original.get('end')),
            event_id=original.get('id'),
            calendar=calendar if calendar else Event.get_calendar_name(calendar_id),
            calendar_id=calendar_id
        )

    @staticmethod
    def equals(event_1: dict, event_2: dict) -> bool:
        keys = ['summary', 'location', 'description', 'start', 'end', 'event_id']
        return any(event_1.get(key) != event_2.get(key) for key in keys)

    @staticmethod
    def get_calendar_name(calendar_id: str):
        calendars = Utils.read_json('data/google/calendars.json')
        hits = [cal_name for cal_name, cal_id in calendars.items() if cal_id == calendar_id]
        return hits[0] if hits else ''
