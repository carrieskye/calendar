from datetime import datetime


class EventDateTime:

    def __init__(self, date_time: datetime, time_zone: str):
        self.date_time = date_time
        self.time_zone = time_zone

    def to_dict(self):
        return {
            'dateTime': self.date_time.isoformat(),
            'timeZone': self.time_zone
        }

    @classmethod
    def get_event_date_time(cls, original: dict):
        return EventDateTime(original.get('date_time'), original.get('time_zone'))
