import re
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class Address(BaseModel):
    address_lines: List[str] = Field(default_factory=list)
    house_no: Optional[str] = Field(None)
    street: Optional[str] = Field(None)
    district: Optional[str] = Field(None)
    postal_code: Optional[str] = Field(None)
    city: Optional[str] = Field(None)
    state: Optional[str] = Field(None)
    country_code: str
    country: str
    original: Optional[str] = Field(None)

    def __str__(self) -> str:
        return ", ".join([x.strip() for x in self.address_parts])

    @property
    def address_parts(self) -> List[str]:
        parts = self.address_lines + [self.street_part, self.district, self.city_part, self.country]
        return [x for x in parts if x and x.strip()]

    @property
    def street_part(self) -> str:
        return f"{self.street} {self.house_no}"

    @property
    def city_part(self) -> str:
        return f"{self.postal_code} {self.city}"

    @model_validator(mode="before")
    def from_string(cls, values: dict) -> dict:
        return values

    @staticmethod
    def parse_other_parts(other_parts: List[str]) -> dict:
        address_lines, house_no, street = [], "", ""
        if other_parts:
            street = other_parts[-1]
            address_lines = other_parts[:-1]

            if re.search(r"[0-9]", street.split()[-1]):
                house_no = street.split(" ")[-1]
                street = " ".join(street.split(" ")[:-1])
            elif re.search(r"[0-9]", street.split()[0]):
                house_no = street.split(" ")[0]
                street = " ".join(street.split(" ")[1:])

            if not house_no:
                address_lines = other_parts
                street = ""

        return {"address_lines": address_lines, "house_no": house_no, "street": street}

    @staticmethod
    def parse_city_and_postal_code(city_and_postal_code: str) -> dict:
        if match := re.fullmatch(r"(?P<postal_code>[0-9 ]+) (?P<city>[^0-9]+)", city_and_postal_code):
            return match.groupdict()
        if match := re.fullmatch(r"(?P<city>[^0-9]+) (?P<postal_code>[0-9 ]+)", city_and_postal_code):
            return match.groupdict()
        return {"postal_code": "", "city": city_and_postal_code}
