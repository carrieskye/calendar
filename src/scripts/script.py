import logging
from abc import ABC, abstractmethod

from src.data import Data
from src.enums import Owner
from src.models.location.geo_location import GeoLocation
from src.utils import Formatter, Input


class Script(ABC):
    def __init__(self) -> None:
        logging.info(Formatter.sub_title("Input"))

    @abstractmethod
    def run(self) -> None:
        logging.info(Formatter.sub_title("Processing"))

    @staticmethod
    def get_owner(default: Owner = Owner.SHARED) -> Owner:
        owner = Input.get_string_input("Calendar owner", input_type="name", default=default.name)
        return Owner.__members__[owner.upper()]

    @staticmethod
    def get_location(default: str = "järnvagsgatan") -> GeoLocation:
        location = Input.get_string_input("Location", input_type="name", default=default)
        return Data.geo_location_dict[location]
