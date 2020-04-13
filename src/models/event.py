from __future__ import annotations

from src.models.calendar import Calendar
from src.models.event_datetime import EventDateTime


class Event:

    def __init__(self, summary: str, location: str, start: EventDateTime, end: EventDateTime, description: str = '',
                 event_id: str = '', calendar: Calendar = None, owner: str = ''):
        self.summary = summary
        self.location = location if location else ''
        self.description = description if description else ''
        self.start = start
        self.end = end
        self.event_id = event_id
        self.calendar = calendar
        self.owner = owner

    def __dict__(self) -> dict:
        return {
            'summary': self.summary,
            'location': self.location,
            'description': self.description,
            'start': self.start.__dict__(),
            'end': self.end.__dict__(),
            'visibility': 'default'
        }

    @classmethod
    def from_dict(cls, original: dict, calendar: Calendar, owner: str) -> Event:
        return cls(
            summary=original.get('summary'),
            location=original.get('location'),
            description=original.get('description'),
            start=EventDateTime.get_event_date_time(original.get('start')),
            end=EventDateTime.get_event_date_time(original.get('end')),
            event_id=original.get('id'),
            calendar=calendar,
            owner=owner
        )
