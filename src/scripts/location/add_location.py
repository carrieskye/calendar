import logging

from pytz import country_timezones

from src.address_parser import AddressParser
from src.data import Data
from src.enums import LocationCategory
from src.models import GeoLocation
from src.utils import Formatter, Input

from .location import LocationScript

logger = logging.getLogger(__name__)


class AddLocation(LocationScript):
    def __init__(self) -> None:
        super().__init__()

        logger.info(Formatter.sub_sub_title("DETAILS"))
        self.label = Input.get_string_input("Label")
        self.category = LocationCategory.from_str(Input.get_string_input("Category"))
        self.short = Input.get_string_input("Short address")
        self.address = Input.get_string_input("Address")

    def run(self) -> None:
        address = AddressParser.run(self.address)
        country_code = address.country_code
        if country_code == "UK":
            country_code = "GB"
        time_zone = country_timezones[country_code][0]

        Data.geo_location_dict.__add__(
            self.label,
            GeoLocation(
                category=self.category,
                label=self.label,
                short=self.short,
                address=address,
                time_zone=time_zone,
            ),
        )

        logger.info("Added")
        return
