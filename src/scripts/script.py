from abc import ABC, abstractmethod

from src.data.data import Calendars, Data
from src.models.calendar import Owner
from src.models.geo_location import GeoLocation
from src.utils.input import Input
from src.utils.output import Output


class Script(ABC):

    @abstractmethod
    def __init__(self):
        Output.make_title('Input')

    @abstractmethod
    def run(self):
        Output.make_title('Processing')

    @staticmethod
    def get_owner(default: Owner = Owner.shared) -> Owner:
        owner = Input.get_string_input('Calendar owner', input_type='name', default=default.name)
        return Owner.__members__[owner]

    @staticmethod
    def get_location(default: str = 'bromsgrove_st') -> GeoLocation:
        location = Input.get_string_input('Location', input_type='name', default=default)
        return Data.geo_location_dict[location]


class Work(Script, ABC):
    pass


class Locations(Script, ABC):
    pass


class Media(Script, ABC):
    calendar = Calendars.leisure
