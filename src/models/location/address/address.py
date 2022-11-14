import re
from typing import List, Optional

from pydantic import BaseModel, root_validator


class Address(BaseModel):
    address_lines: List[str]
    house_no: Optional[str]
    street: Optional[str]
    district: Optional[str]
    postal_code: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country_code: Optional[str]
    country: Optional[str]
    original: Optional[str]

    def __str__(self) -> str:
        return ", ".join([x.strip() for x in self.address_parts if x and x.strip()])

    @property
    def address_parts(self) -> List[str]:
        return self.address_lines + [self.street_part, self.district, self.city_part, self.country]

    @property
    def street_part(self) -> str:
        return f"{self.street} {self.house_no}"

    @property
    def city_part(self) -> str:
        return f"{self.postal_code} {self.city}"

    @root_validator(pre=True)
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
        elif match := re.fullmatch(r"(?P<city>[^0-9]+) (?P<postal_code>[0-9 ]+)", city_and_postal_code):
            return match.groupdict()
        else:
            return {"postal_code": "", "city": city_and_postal_code}
