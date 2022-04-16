from __future__ import annotations

from datetime import datetime

from dateutil import tz
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


class EventDateTime:
    def __init__(self, date_time: datetime, time_zone: str):
        self.date_time = date_time
        self.time_zone = time_zone if time_zone else ""

    def __str__(self) -> str:
        return f"{self.date_time} ({self.time_zone})"

    def serialise_for_google(self) -> dict:
        return {"dateTime": self.date_time.isoformat(), "timeZone": self.time_zone}

    def correct_time_zone(self):
        date_time_with_tz = self.date_time.replace(tzinfo=tz.gettz(self.time_zone))
        if self.date_time != date_time_with_tz:
            hours_neg, minutes_neg, seconds_neg = [int(x) for x in str(self.date_time.utcoffset()).split(":")]
            self.date_time = self.date_time.replace(tzinfo=tz.gettz(self.time_zone))
            hours_pos, minutes_pos, seconds_pos = [int(x) for x in str(date_time_with_tz.utcoffset()).split(":")]
            self.date_time += relativedelta(hours=hours_pos, minutes=minutes_pos, seconds=seconds_pos)
            self.date_time -= relativedelta(hours=hours_neg, minutes=minutes_neg, seconds=seconds_neg)

    @classmethod
    def from_dict(cls, original: dict) -> EventDateTime:
        return EventDateTime(date_time=parse(original.get("dateTime")), time_zone=original.get("timeZone"))
