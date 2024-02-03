__all__ = ["TimingItem"]

from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator
from skye_comlib.utils.formatter import Formatter

from src.data.data import Data
from src.models.calendar import Calendar
from src.models.location.geo_location import GeoLocation
from src.models.timing.timing_notes import TimingNotes


class TimingItem(BaseModel):
    id: int = Field(alias="ID")
    duration: timedelta = Field(alias="Duration")
    start_date: datetime = Field(alias="Start Date")
    end_date: datetime = Field(alias="End Date")
    original_title: str = Field(alias="Title")
    notes: TimingNotes = Field(alias="Notes")
    all_projects: List[str] = Field(alias="Project")

    @field_validator("duration", mode="before")
    def parse_duration(cls, value: str | timedelta) -> timedelta:
        if isinstance(value, timedelta):
            return value
        t = datetime.strptime(value, "%H:%M:%S")
        return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)

    @field_validator("notes", mode="before")
    def parse_notes(cls, value: str | TimingNotes) -> TimingNotes:
        if isinstance(value, TimingNotes):
            return value
        value = Formatter.de_serialise_details(value)
        return TimingNotes.model_validate(value)

    @field_validator("all_projects", mode="before")
    def parse_projects(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, list):
            return value
        return value.split(" ▸ ")

    @property
    def projects(self) -> List[str]:
        return self.all_projects[2:] + [self.original_title]

    @property
    def calendar(self) -> Calendar:
        return Data.calendar_dict[self.all_projects[0].lower()]

    def get_location(self) -> Optional[GeoLocation]:
        if self.notes.trajectory:
            return Data.geo_location_dict[self.notes.trajectory.origin]
        if self.notes.location:
            return Data.geo_location_dict[self.notes.location]
        return None

    @property
    def title(self) -> str:
        options = [x for x in self.all_projects if x not in Data.projects_to_ignore + ["Various"]]
        if len(options) > 1:
            return options[1]
        return self.original_title
