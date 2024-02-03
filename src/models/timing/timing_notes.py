__all__ = ["TimingNotes"]

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.enums.transport_mode import TransportMode
from src.models.timing.timing_trajectory import TimingTrajectory


class TimingNotes(BaseModel):
    details: Optional[str] = Field(None)
    location: Optional[str] = Field(None)
    shared: Optional[bool] = Field(None)
    trajectory: Optional[TimingTrajectory] = Field(None)
    transport: Optional[TransportMode] = Field(None)
    url: Optional[str] = Field(None)
    episode: Optional[str] = Field(None)
    year: Optional[str] = Field(None)

    @field_validator("trajectory", mode="before")
    def parse_trajectory(cls, value: str | TimingTrajectory) -> TimingTrajectory:
        if isinstance(value, TimingTrajectory):
            return value
        origin, destination = value.split(" > ")
        return TimingTrajectory(origin=origin, destination=destination)
