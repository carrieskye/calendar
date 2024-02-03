from typing import Optional

from pydantic import BaseModel, Field

from src.models.calendar import Calendar, Owner
from src.models.event_datetime import EventDateTime


class Event(BaseModel):
    summary: str
    location: Optional[str] = Field(None)
    description: str = Field("")
    start: EventDateTime
    end: EventDateTime
    event_id: str = Field("")
    calendar: Optional[Calendar] = Field(None)
    owner: Optional[Owner] = Field(None)

    def serialise_for_google(self) -> dict:
        return {
            "summary": self.summary,
            "location": self.location,
            "description": self.description,
            "start": self.start.serialise_for_google(),
            "end": self.end.serialise_for_google(),
            "visibility": "default",
        }

    @classmethod
    def from_dict(cls, original: dict, calendar: Calendar, owner: Owner) -> "Event":
        return cls(
            summary=original["summary"],
            location=original.get("location"),
            description=original.get("description", ""),
            start=EventDateTime.from_dict(original["start"]),
            end=EventDateTime.from_dict(original["end"]),
            event_id=original.get("id", ""),
            calendar=calendar,
            owner=owner,
        )
