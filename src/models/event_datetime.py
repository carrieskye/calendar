from __future__ import annotations

from datetime import datetime

from dateutil.parser import parse


class EventDateTime:

    def __init__(self, date_time: datetime, time_zone: str):
        self.date_time = date_time
        self.time_zone = time_zone if time_zone else ''

    def __str__(self) -> str:
        return f'{self.date_time} ({self.time_zone})'

    def serialise_for_google(self) -> dict:
        return {
            'dateTime': self.date_time.isoformat(),
            'timeZone': self.time_zone
        }

    @classmethod
    def from_dict(cls, original: dict) -> EventDateTime:
        return EventDateTime(date_time=parse(original.get('dateTime')), time_zone=original.get('timeZone'))
