from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator
from pytz import country_timezones

from src.address_parser import AddressParser
from src.enums import LocationCategory
from src.utils import File

from ..location_timestamp import LocationTimestamp
from .address import Address
from .bounding_box import BoundingBox

_BB_KEYS = ("min_latitude", "max_latitude", "min_longitude", "max_longitude")


class GeoLocation(BaseModel):
    time_zone: str
    category: LocationCategory
    label: str
    short: str
    address: Address
    bounding_box: BoundingBox | None = Field(default=None)

    @field_validator("category", mode="before")
    @classmethod
    def parse_category(cls, value: str | LocationCategory | int) -> LocationCategory:
        if isinstance(value, LocationCategory):
            return value
        if isinstance(value, str):
            return LocationCategory.from_str(value)
        if isinstance(value, int):
            # Handle integer values from auto() in older serializations
            for member in LocationCategory:
                if member.value == value:
                    return member
            raise ValueError(f"No LocationCategory enum member with value {value}")
        raise TypeError(f"Cannot convert {type(value).__name__} to LocationCategory")

    @field_validator("bounding_box", mode="before")
    @classmethod
    def parse_bounding_box(cls, value: dict | BoundingBox | None) -> BoundingBox | None:
        if isinstance(value, BoundingBox):
            return value
        if isinstance(value, dict):
            return BoundingBox(**value)
        return None

    @model_validator(mode="before")
    def from_dict(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        addr = values.get("address")
        if isinstance(addr, dict):
            values["address"] = Address.model_validate(addr)
        elif isinstance(addr, str):
            values["address"] = AddressParser.run(addr)
        elif not isinstance(addr, Address):
            raise TypeError(f"address must be dict, str, or Address, got {type(addr).__name__}")
        if not values.get("time_zone"):
            country_code = values["address"].country_code
            if country_code == "UK":
                country_code = "GB"
            values["time_zone"] = country_timezones[country_code][0]
        # Extract individual bounding box columns from CSV rows into a nested dict
        if not values.get("bounding_box") and all(values.get(k) for k in _BB_KEYS):
            values["bounding_box"] = {k: float(values[k]) for k in _BB_KEYS}
        for k in _BB_KEYS:
            values.pop(k, None)
        return {k: v for k, v in values.items() if k not in ["country", "city"]}

    def to_dict(self) -> dict:
        return {
            "time_zone": self.time_zone,
            "country": self.address.country,
            "city": self.address.city,
            "category": self.category.name.lower(),
            "label": self.label,
            "short": self.short,
            "address": self.address.original,
            "min_latitude": self.bounding_box.min_latitude if self.bounding_box else "",
            "max_latitude": self.bounding_box.max_latitude if self.bounding_box else "",
            "min_longitude": self.bounding_box.min_longitude if self.bounding_box else "",
            "max_longitude": self.bounding_box.max_longitude if self.bounding_box else "",
        }

    def within_bounding_box(self, location_timestamp: LocationTimestamp) -> bool:
        """Returns True if the location timestamp's coordinates fall within this location's bounding box."""
        if not self.bounding_box:
            return False
        return self.bounding_box.contains(location_timestamp.latitude, location_timestamp.longitude)

    @classmethod
    def build_from_csv(cls, csv_file_path: Path) -> list["GeoLocation"]:
        return [GeoLocation(**x) for x in File.read_csv(csv_file_path)]
