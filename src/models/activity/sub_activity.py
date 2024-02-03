__all__ = ["SubActivity"]

from typing import List

from pydantic import BaseModel

from src.models.event_datetime import EventDateTime


class SubActivity(BaseModel):
    activity_id: int
    projects: List[str]
    start: EventDateTime
    end: EventDateTime

    def __str__(self) -> str:
        self.start.correct_time_zone()
        self.end.correct_time_zone()
        period = f"{self.start.date_time.strftime('%H:%M:%S')} - {self.end.date_time.strftime('%H:%M:%S')}"
        title = " ▸ ".join(self.projects)
        return f"{period}: {title}"
