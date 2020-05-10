from datetime import time, datetime

from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Calendars
from src.models.calendar import Owner
from src.scripts.script import Work
from src.utils.input import Input


class CopyToLarry(Work):

    def __init__(self):
        super().__init__()

        start = Input.get_date_input('Start')
        self.day = datetime.combine(start, time(4, 0))
        self.end = self.day + relativedelta(days=Input.get_int_input('Days', '#days') - 1)

    def run(self):
        super().run()

        while self.day <= self.end:
            next_day = self.day + relativedelta(days=1)

            for calendar in [Calendars.food, Calendars.work]:
                for event in GoogleCalAPI.get_events(calendar, Owner.larry, 1000, self.day, next_day):
                    GoogleCalAPI.delete_event(calendar.larry, event.event_id)

                for event in GoogleCalAPI.get_events(calendar, Owner.carrie, 1000, self.day, next_day):
                    event.description = ''
                    GoogleCalAPI.create_event(calendar.larry, event)

            self.day += relativedelta(days=1)
