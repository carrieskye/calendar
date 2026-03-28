import pycountry

from src.models.location.address import (
    Address,
    ATAddress,
    BEAddress,
    CHAddress,
    DEAddress,
    DKAddress,
    FRAddress,
    NOAddress,
    SEAddress,
    UKAddress,
)


class AddressParser:
    country_address_parser_lookup: dict[str, type[Address]] = {
        "AT": ATAddress,
        "BE": BEAddress,
        "CH": CHAddress,
        "DE": DEAddress,
        "DK": DKAddress,
        "FR": FRAddress,
        "NO": NOAddress,
        "SE": SEAddress,
        "UK": UKAddress,
        "GB": UKAddress,
    }

    @classmethod
    def run(cls, address_str: str) -> Address:
        country = address_str.split(", ")[-1].replace("UK", "United Kingdom")
        country_code = pycountry.countries.lookup(country).alpha_2

        if address_parser := cls.country_address_parser_lookup[country_code.upper()]:
            return address_parser(original=address_str)

        raise Exception("Invalid country")
