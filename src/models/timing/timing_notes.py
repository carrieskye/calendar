from pydantic import BaseModel, Field, field_validator

from src.enums import TransportMode

from .timing_trajectory import TimingTrajectory


class TimingNotes(BaseModel):
    details: str | None = Field(default=None)
    location: str | None = Field(default=None)
    shared: bool | None = Field(default=None)
    trajectory: TimingTrajectory | None = Field(default=None)
    transport: TransportMode | None = Field(default=None)
    url: str | None = Field(default=None)
    episode: str | None = Field(default=None)
    year: str | None = Field(default=None)

    @field_validator("transport", mode="before")
    @classmethod
    def parse_transport(cls, value: str | TransportMode | int | None) -> TransportMode | None:
        if value is None or isinstance(value, TransportMode):
            return value
        if isinstance(value, str):
            return TransportMode.from_str(value)
        if isinstance(value, int):
            # Handle integer values from auto() in older serializations
            for member in TransportMode:
                if member.value == value:
                    return member
            raise ValueError(f"No TransportMode enum member with value {value}")
        raise TypeError(f"Cannot convert {type(value).__name__} to TransportMode")

    @field_validator("trajectory", mode="before")
    def parse_trajectory(cls, value: str | TimingTrajectory) -> TimingTrajectory:
        if isinstance(value, TimingTrajectory):
            return value
        origin, destination = value.split(" > ")
        return TimingTrajectory(origin=origin, destination=destination)
