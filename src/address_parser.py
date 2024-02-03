from typing import Dict, Type

import pycountry

from src.models.location.address.address import Address
from src.models.location.address.at_address import ATAddress
from src.models.location.address.be_address import BEAddress
from src.models.location.address.ch_address import CHAddress
from src.models.location.address.de_address import DEAddress
from src.models.location.address.dk_address import DKAddress
from src.models.location.address.fr_address import FRAddress
from src.models.location.address.no_address import NOAddress
from src.models.location.address.se_address import SEAddress
from src.models.location.address.uk_address import UKAddress


class AddressParser:
    country_address_parser_lookup: Dict[str, Type[Address]] = {
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
