from datetime import datetime

from dateutil import tz  # type: ignore
from dateutil.parser import parse  # type: ignore
from dateutil.relativedelta import relativedelta  # type: ignore
from pydantic import BaseModel


class EventDateTime(BaseModel):
    date_time: datetime
    time_zone: str

    def __str__(self) -> str:
        return f"{self.date_time} ({self.time_zone})"

    def serialise_for_google(self) -> dict:
        return {"dateTime": self.date_time.isoformat(), "timeZone": self.time_zone}

    def correct_time_zone(self) -> None:
        date_time_with_tz = self.date_time.replace(tzinfo=tz.gettz(self.time_zone))
        if self.date_time != date_time_with_tz:
            hours_neg, minutes_neg, seconds_neg = [int(x) for x in str(self.date_time.utcoffset()).split(":")]
            self.date_time = self.date_time.replace(tzinfo=tz.gettz(self.time_zone))
            hours_pos, minutes_pos, seconds_pos = [int(x) for x in str(date_time_with_tz.utcoffset()).split(":")]
            self.date_time += relativedelta(hours=hours_pos, minutes=minutes_pos, seconds=seconds_pos)
            self.date_time -= relativedelta(hours=hours_neg, minutes=minutes_neg, seconds=seconds_neg)

    @classmethod
    def from_dict(cls, original: dict) -> "EventDateTime":
        return EventDateTime(date_time=parse(original.get("dateTime")), time_zone=original.get("timeZone", ""))
