import logging
from abc import ABC, abstractmethod

from src.data.data import Data
from src.models.calendar import Owner
from src.models.location.geo_location import GeoLocation
from src.utils.formatting import Formatter
from src.utils.prompts import Input


class Script(ABC):
    def __init__(self) -> None:
        logging.info(Formatter.sub_title("Input"))

    @abstractmethod
    def run(self) -> None:
        logging.info(Formatter.sub_title("Processing"))

    @staticmethod
    def get_owner(default: Owner = Owner.shared) -> Owner:
        owner = Input.get_string_input("Calendar owner", input_type="name", default=default.name)
        return Owner.__members__[owner]

    @staticmethod
    def get_location(default: str = "järnvagsgatan") -> GeoLocation:
        location = Input.get_string_input("Location", input_type="name", default=default)
        return Data.geo_location_dict[location]
