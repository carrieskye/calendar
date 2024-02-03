import re
from typing import List

from pydantic import model_validator

from src.models.location.address.address import Address

UK_STREET_ABBR = [
    "Ave",
    "Blvd",
    "Bdwy",
    "Cir",
    "Cl",
    "Ct",
    "Cr",
    "Dr",
    "Gdn",
    "Gdns",
    "Gn",
    "Gr",
    "J",
    "Ln",
    "Mt",
    "Pl",
    "Pk",
    "Rdg",
    "Rd",
    "St.",
    "Sq",
    "Square",
    "St",
    "Ter",
    "Val",
    "Way",
]


class UKAddress(Address):
    @property
    def street_part(self) -> str:
        return f"{self.house_no} {self.street}"

    @property
    def city_part(self) -> str:
        return f"{self.city} {self.postal_code}"

    @model_validator(mode="before")
    def from_string(cls, values: dict) -> dict:
        address_split = values["original"].split(", ")
        values.update(cls.parse_other_parts(address_split[:-2]))
        values.update(cls.parse_city_and_postal_code(address_split[-2]))
        values["country_code"] = "UK"
        values["country"] = "UK"
        return values

    @staticmethod
    def parse_other_parts(other_parts: List[str]) -> dict:
        address_lines, street, house_no, district = [], "", "", [""]
        if other_parts:
            street_part_indices = [
                idx
                for idx, x in enumerate(other_parts)
                if x[0].isdigit() or any(x.endswith(" " + street_abbr) for street_abbr in UK_STREET_ABBR)
            ]
            if (
                len(street_part_indices) > 1
                and len(street_part_indices) == 2
                and street_part_indices[0] + 1 == street_part_indices[1]
            ):
                street_part_indices.pop(0)

            if len(street_part_indices) > 1:
                raise NotImplementedError(f"Too many street parts for {other_parts}: {street_part_indices}")

            if street_part_indices:
                index = street_part_indices[0]
                address_lines = other_parts[:index]
                street = other_parts[index]
                if index + 1 > len(other_parts):
                    district = other_parts[index:]
            else:
                if len(other_parts[-1].split()) == 1 or (
                    len(other_parts[-1].split()) == 2 and other_parts[-1].startswith("St")
                ):
                    district = [other_parts.pop(-1)]
                address_lines = other_parts

            if street and str.isdigit(street[0]):
                house_no = street.split(" ")[0]
                street = " ".join(street.split(" ")[1:])

            if len(district) > 1:
                raise Exception(f"Can only add one district: {district}")
        return {"address_lines": address_lines, "house_no": house_no, "street": street, "district": district[0]}

    @staticmethod
    def parse_city_and_postal_code(city_and_postal_code: str) -> dict:
        if match := re.fullmatch(
            r"(?P<city>[^0-9]+) (?P<postal_code>[A-Z]{2}[0-9][0-9A-Z]?(\s[0-9][A-Z]{2})?)",
            city_and_postal_code,
        ):
            return match.groupdict()
        return {"postal_code": "", "city": city_and_postal_code}
