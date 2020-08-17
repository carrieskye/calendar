from datetime import datetime, time

from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Calendars
from src.models.calendar import Owner
from src.scripts.work.work import WorkScript
from src.utils.input import Input
from src.utils.logger import Logger


class UpdateProject(WorkScript):

    def __init__(self):
        super().__init__()

        start = Input.get_date_input('Start')
        days = Input.get_int_input(name='Days', input_type='#days')

        self.start = datetime.combine(start, time(4, 0))
        self.end = self.start + relativedelta(days=days)
        self.project = Input.get_string_input(name='Project', default='Analyse')

    def run(self):
        Logger.sub_title('Processing')

        events = GoogleCalAPI.get_events(Calendars.work, Owner.carrie, 1000, self.start, self.end)
        for event in events:
            event.summary = 'Amplyfi'
            event.description = self.project
            GoogleCalAPI.update_event(Calendars.work.carrie, event.event_id, event)
