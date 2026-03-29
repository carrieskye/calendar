from pydantic import BaseModel, model_validator

from ..point import Point


class BoundingBox(BaseModel):
    min_latitude: float
    max_latitude: float
    min_longitude: float
    max_longitude: float

    @model_validator(mode="after")
    def validate_ranges(self) -> "BoundingBox":
        if self.min_latitude > self.max_latitude:
            raise ValueError(f"min_latitude ({self.min_latitude}) must be <= max_latitude ({self.max_latitude})")
        if self.min_longitude > self.max_longitude:
            raise ValueError(f"min_longitude ({self.min_longitude}) must be <= max_longitude ({self.max_longitude})")
        return self

    @property
    def intersection(self) -> Point:
        """Returns the center point where the bounding box diagonals intersect."""
        return Point(
            latitude=(self.min_latitude + self.max_latitude) / 2,
            longitude=(self.min_longitude + self.max_longitude) / 2,
        )

    def contains(self, latitude: float, longitude: float) -> bool:
        """Returns True if the given coordinates fall within this bounding box."""
        return (
            self.min_latitude <= latitude <= self.max_latitude and self.min_longitude <= longitude <= self.max_longitude
        )
