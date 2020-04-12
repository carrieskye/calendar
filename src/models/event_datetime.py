from __future__ import annotations

from datetime import datetime

from dateutil.parser import parse


class EventDateTime:

    def __init__(self, date_time: datetime, time_zone: str):
        self.date_time = date_time
        self.time_zone = time_zone if time_zone else ''

    def to_dict(self):
        return {
            'dateTime': self.date_time.isoformat(),
            'timeZone': self.time_zone
        }

    @classmethod
    def get_event_date_time(cls, original: dict) -> EventDateTime:
        return EventDateTime(date_time=parse(original.get('dateTime')), time_zone=original.get('timeZone'))
