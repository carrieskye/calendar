import os
import re
from datetime import time, datetime

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Calendars
from src.models.calendar import Owner
from src.models.event import Event
from src.models.event_datetime import EventDateTime
from src.scripts.activity.activity import ActivityScript
from src.utils.file import File
from src.utils.input import Input
from src.utils.logger import Logger


class ParseHayleyExportScript(ActivityScript):
    long_categories = {
        'bath': 'Bath',
        'bf': 'Breastfeeding',
        'bm': 'Breast milk',
        'exp': 'Expressing',
        'for': 'Formula',
        'nap': 'Nap',
        'np': 'Nappy',
        'slbf': 'Breastfeeding + sleeping',
        'str': 'Sleep training'
    }

    def __init__(self):
        super().__init__()

        start = Input.get_date_input('Start')
        self.start = datetime.combine(start, time(4, 0))
        days = Input.get_int_input('Days', '#days')
        self.end = self.start + relativedelta(days=days)
        self.owner = self.get_owner()
        self.location = self.get_location()

    def run(self):
        super().run()

        events = GoogleCalAPI.get_events(Calendars.chores, Owner.shared, 1000, self.start, self.end)
        for event in events:
            GoogleCalAPI.delete_event(Calendars.chores.shared, event.event_id)

        self.create_events()

    def create_events(self):
        for file in os.listdir('data/hayley'):
            if not file.endswith('.csv'):
                continue
            export = File.read_csv(f'data/hayley/{file}', log=False)
            category = re.match(r'Hayley - (?P<category>[a-z]*).csv', file).group('category')
            for item in export:
                start = parse(item['actual'] + ' ' + item['start'])
                if not self.start < start < self.end:
                    continue
                hours, minutes = item['total'].split(':')
                end = start + relativedelta(hours=int(hours), minutes=int(minutes))
                event = Event(
                    summary=self.long_categories[category],
                    location=self.location.address.__str__(),
                    start=EventDateTime(start, self.location.time_zone),
                    end=EventDateTime(end, self.location.time_zone)
                )
                Logger.log(event.summary)
                GoogleCalAPI.create_event(Calendars.chores.shared, event)
