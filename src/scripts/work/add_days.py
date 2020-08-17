from datetime import time

from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Calendars, GeoLocations
from src.models.event import Event
from src.models.event_datetime import EventDateTime
from src.models.geo_location import GeoLocation
from src.scripts.work.work import Work
from src.utils.input import Input


class AddDays(Work):

    def __init__(self):
        super().__init__()

        self.day = Input.get_date_input('Start')
        self.end = self.day + relativedelta(days=Input.get_int_input('Days', '#days') - 1)
        self.skating = Input.get_bool_input('Skating')
        self.location = self.get_location()

    def run(self):
        super().run()

        while self.day <= self.end:
            if self.day.weekday() == 7 or self.day.weekday() < 5:
                if self.skating:
                    viola = GeoLocations.viola_arena
                    self.create_event(Calendars.sports.shared, 'Ice skating', viola, time(8), time(9))

                # self.create_event(Calendars.work.carrie, 'Amplyfi', self.location, start=time(10), end=time(12))
                self.create_event(Calendars.work.larry, 'Delio', self.location, start=time(9), end=time(12))
                # self.create_event(Calendars.food.carrie, 'Lunch', self.location, time(12), time(13))
                self.create_event(Calendars.food.larry, 'Lunch', self.location, time(12), time(12, 30))
                # self.create_event(Calendars.work.carrie, 'Amplyfi', self.location, start=time(13), end=time(17))
                self.create_event(Calendars.work.larry, 'Delio', self.location, start=time(12, 30), end=time(17, 30))
                self.create_event(Calendars.food.larry, 'Dinner', self.location, time(17, 30), time(18, 30))
                self.create_event(Calendars.projects.larry, 'YouTube', self.location, start=time(18, 30), end=time(20))

            self.day += relativedelta(days=1)

    def create_event(self, cal_id: str, summary: str, location: GeoLocation, start: time, end: time, desc: str = ''):
        event = Event(
            summary=summary,
            location=location.address.__str__(),
            description=desc,
            start=EventDateTime(
                date_time=self.day + relativedelta(hours=start.hour, minutes=start.minute),
                time_zone=location.time_zone),
            end=EventDateTime(
                date_time=self.day + relativedelta(hours=end.hour, minutes=end.minute),
                time_zone=location.time_zone)
        )
        GoogleCalAPI.create_event(cal_id, event)
