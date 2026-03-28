from pathlib import Path
from typing import Any, List

from pydantic import BaseModel, model_validator
from pytz import country_timezones  # type: ignore

from src.address_parser import AddressParser
from src.enums.location_category import LocationCategory
from src.models.location.address.address import Address
from src.utils.file_io import File


class GeoLocation(BaseModel):
    time_zone: str
    category: LocationCategory
    label: str
    short: str
    address: Address

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
            values["time_zone"] = country_timezones(country_code)[0]
        return {k: v for k, v in values.items() if k not in ["country", "city"]}

    def to_dict(self) -> dict:
        return {
            "time_zone": self.time_zone,
            "country": self.address.country,
            "city": self.address.city,
            "category": self.category,
            "label": self.label,
            "short": self.short,
            "address": self.address.original,
        }

    @classmethod
    def build_from_csv(cls, csv_file_path: Path) -> List["GeoLocation"]:
        return [GeoLocation(**x) for x in File.read_csv(csv_file_path)]
