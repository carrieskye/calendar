from pydantic import model_validator

from src.models.location.address.address import Address


class BEAddress(Address):
    @model_validator(mode="before")
    def from_string(cls, values: dict) -> dict:
        address_split = values["original"].split(", ")
        values.update(cls.parse_other_parts(address_split[:-2]))
        values.update(cls.parse_city_and_postal_code(address_split[-2]))
        values["country_code"] = "BE"
        values["country"] = "Belgium"
        return values
