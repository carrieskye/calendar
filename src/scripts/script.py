from abc import ABC, abstractmethod

from src.data.data import Calendars
from src.utils.media import MediaUtils
from src.utils.output import Output


class Script(ABC):

    @abstractmethod
    def __init__(self):
        Output.make_title('Input')

    @abstractmethod
    def run(self):
        Output.make_title('Processing')


class Work(Script, ABC):
    time_zone = 'Europe/London'


class Media(Script):

    def __init__(self):
        super().__init__()

        self.utils = MediaUtils()

        self.calendar = Calendars.leisure
        self.owner = 'shared'
        self.location = 'bromsgrove'
        self.time_zone = 'Europe/London'
        self.gap = 30

    @abstractmethod
    def run(self):
        pass


class Locations(Script, ABC):
    pass
