import pycountry
from pytz import country_timezones
from skye_comlib.utils.input import Input

from src.models.location.address.at_address import ATAddress
from src.models.location.address.be_address import BEAddress
from src.models.location.address.ch_address import CHAddress
from src.models.location.address.de_address import DEAddress
from src.models.location.address.fr_address import FRAddress
from src.models.location.address.no_address import NOAddress
from src.models.location.address.se_address import SEAddress
from src.models.location.address.uk_address import UKAddress


class AddressParser:
    country_address_parser_lookup = {
        "AT": ATAddress,
        "BE": BEAddress,
        "CH": CHAddress,
        "DE": DEAddress,
        "FR": FRAddress,
        "NO": NOAddress,
        "SE": SEAddress,
        "UK": UKAddress,
        "GB": UKAddress,
    }

    @classmethod
    def run(cls, address_str: str):
        country = address_str.split(", ")[-1].replace("UK", "United Kingdom")
        country_code = pycountry.countries.lookup(country).alpha_2

        if country_code in cls.country_address_parser_lookup.keys():
            address = cls.country_address_parser_lookup[country_code.upper()](original=address_str)
            return address

        raise Exception("Invalid country")
