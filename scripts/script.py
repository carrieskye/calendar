from abc import ABC, abstractmethod

from src.connectors.google_calendar import GoogleCalendarAPI
from src.connectors.trakt import TraktAPI
from src.utils.output import Output


class Script(ABC):

    @abstractmethod
    def run(self):
        pass


class Work(Script):

    def __init__(self):
        Output.make_title('Input')
        self.google_cal = GoogleCalendarAPI()

        self.cal_id_food = self.google_cal.get_calendar_id('food_shared')
        self.cal_id_sports = self.google_cal.get_calendar_id('sports_shared')
        self.cal_id_work = self.google_cal.get_calendar_id('work')
        self.cal_id_work_larry = self.google_cal.get_calendar_id('work_larry')

        self.time_zone = 'Europe/London'

    @abstractmethod
    def run(self):
        pass


class Media(Script):

    def __init__(self):
        Output.make_title('Input')
        self.trakt_api = TraktAPI()
        self.google_cal = GoogleCalendarAPI()

        self.calendar = 'tv_shared'
        self.location = 'bromsgrove'
        self.time_zone = 'Europe/London'
        self.gap = 30

    @abstractmethod
    def run(self):
        pass
