from pathlib import Path
from typing import List

from pydantic import BaseModel, root_validator
from skye_comlib.utils.file import File

from src.address_parser import AddressParser
from src.models.location.address.address import Address


class GeoLocation(BaseModel):
    time_zone: str
    category: str
    label: str
    short: str
    address: Address

    @root_validator(pre=True)
    def from_dict(cls, values: dict) -> dict:
        values["address"] = AddressParser.run(values["address"])
        values.pop("country")
        values.pop("city")
        return values

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
