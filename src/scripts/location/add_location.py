import logging

from pytz import country_timezones
from skye_comlib.utils.formatter import Formatter
from skye_comlib.utils.input import Input

from src.address_parser import AddressParser
from src.data.data import Data
from src.models.location.geo_location import GeoLocation
from src.scripts.location.location import LocationScript


class AddLocation(LocationScript):
    def __init__(self):
        super().__init__()

        logging.info(Formatter.sub_sub_title("DETAILS"))
        self.label = Input.get_string_input("Label")
        self.category = Input.get_string_input("Category")
        self.short = Input.get_string_input("Short address")
        self.address = Input.get_string_input("Address")

    def run(self):
        address = AddressParser.run(self.address)
        time_zone = country_timezones(address.country_code)[0]
        time_zone = Input.get_string_input("Time zone", "country/city", time_zone)

        Data.geo_location_dict.__add__(
            self.label,
            GeoLocation(
                time_zone=time_zone, category=self.category, label=self.label, short=self.short, address=address
            ),
        )

        logging.info("Added")
        return
