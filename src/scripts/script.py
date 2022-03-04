import logging
from abc import ABC, abstractmethod

from skye_comlib.utils.formatter import Formatter
from skye_comlib.utils.input import Input

from src.data.data import Data
from src.models.calendar import Owner
from src.models.geo_location import GeoLocation


class Script(ABC):
    @abstractmethod
    def __init__(self):
        logging.info(Formatter.sub_title("Input"), extra={"markup": True})

    @abstractmethod
    def run(self):
        print()
        logging.info(Formatter.sub_title("Processing"), extra={"markup": True})

    @staticmethod
    def get_owner(default: Owner = Owner.shared) -> Owner:
        owner = Input.get_string_input(
            "Calendar owner", input_type="name", default=default.name,
        )
        return Owner.__members__[owner]

    @staticmethod
    def get_location(default: str = "talygarn_st") -> GeoLocation:
        location = Input.get_string_input(
            "Location", input_type="name", default=default,
        )
        return Data.geo_location_dict[location]
