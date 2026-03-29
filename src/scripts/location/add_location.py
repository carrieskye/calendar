import logging

from src.data import Data
from src.models.location.geo_location import GeoLocation
from src.utils import Formatter, Input

from .location import LocationScript

logger = logging.getLogger(__name__)


class AddLocation(LocationScript):
    def __init__(self) -> None:
        super().__init__()

        logger.info(Formatter.sub_sub_title("DETAILS"))
        self.label = Input.get_string_input("Label")
        self.category = Input.get_string_input("Category")
        self.short = Input.get_string_input("Short address")
        self.address = Input.get_string_input("Address")

    def run(self) -> None:
        Data.geo_location_dict.__add__(
            self.label,
            GeoLocation(category=self.category, label=self.label, short=self.short, address=self.address),
        )

        logger.info("Added")
        return
