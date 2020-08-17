from abc import ABC, abstractmethod
from inspect import getframeinfo, stack

from src.data.data import Data
from src.models.calendar import Owner
from src.models.geo_location import GeoLocation
from src.utils.input import Input
from src.utils.logger import Logger


class Script(ABC):

    @abstractmethod
    def __init__(self):
        Logger.sub_title('Input')

    @abstractmethod
    def run(self):
        Logger.sub_title('Processing')

    @staticmethod
    def get_owner(default: Owner = Owner.shared) -> Owner:
        owner = Input.get_string_input(
            'Calendar owner',
            input_type='name',
            default=default.name,
            caller=getframeinfo(stack()[1][0])
        )
        return Owner.__members__[owner]

    @staticmethod
    def get_location(default: str = 'talygarn_st') -> GeoLocation:
        location = Input.get_string_input(
            'Location',
            input_type='name',
            default=default,
            caller=getframeinfo(stack()[1][0])
        )
        return Data.geo_location_dict[location]
