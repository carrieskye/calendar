from datetime import time

from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Calendars, GeoLocations
from src.models.event import Event
from src.models.event_datetime import EventDateTime
from src.models.geo_location import GeoLocation
from src.scripts.script import Work
from src.utils.input import Input
from src.utils.output import Output


class AddDays(Work):

    def __init__(self):
        super().__init__()

        self.day = Input.get_date_input('Start')
        self.end = self.day + relativedelta(days=Input.get_int_input('Days', '#days') - 1)
        self.project = Input.get_string_input('Project', default='Analyze')
        self.skating = Input.get_bool_input('Skating')

    def run(self):
        super().run()

        while self.day <= self.end:
            if self.day.weekday() == 7 or self.day.weekday() < 5:
                if self.skating:
                    self.create_event(
                        cal_id=Calendars.sports.shared, summary='Ice skating',
                        location=GeoLocations.viola_arena, start=time(8), end=time(9))

                location = GeoLocations.bromsgrove_st
                self.create_work_event(location=location, start=time(10), end=time(12, 30))
                self.create_lunch_event(location=location, start=time(12, 30), end=time(13, 30))
                self.create_work_event(location=location, start=time(13, 30), end=time(17))

            self.day += relativedelta(days=1)

        Output.make_bold('Added work days\n')

    def create_work_event(self, location: GeoLocation, start: time, end: time):
        for calendar in [Calendars.work.carrie, Calendars.work.larry]:
            desc = self.project if calendar == Calendars.work.carrie else ''
            self.create_event(cal_id=calendar, summary='Amplyfi', location=location, start=start, end=end, desc=desc)

    def create_lunch_event(self, location: GeoLocation, start: time, end: time):
        for calendar in [Calendars.food.carrie, Calendars.food.larry]:
            self.create_event(cal_id=calendar, summary='Lunch', location=location, start=start, end=end)

    def create_event(self, cal_id: str, summary: str, location: GeoLocation, start: time, end: time,
                     desc: str = ''):
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
