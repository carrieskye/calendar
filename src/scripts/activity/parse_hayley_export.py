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
        for category in ['breastfeeding', 'formula', 'breast milk', 'expressed', 'nappies', 'bath', 'str', 'nap']:
            export = File.read_csv(f'data/hayley/Hayley - {category}.csv', log=False)
            for item in export:
                start = parse(item['actual'] + ' ' + item['start'])
                if not self.start < start < self.end:
                    continue
                hours, minutes = item['total'].split(':')
                end = start + relativedelta(hours=int(hours), minutes=int(minutes))
                event = Event(
                    summary=self.get_summary(category),
                    location=self.location.address.__str__(),
                    start=EventDateTime(start, self.location.time_zone),
                    end=EventDateTime(end, self.location.time_zone)
                )
                Logger.log(event.summary)
                GoogleCalAPI.create_event(Calendars.chores.shared, event)

    @staticmethod
    def get_summary(category: str) -> str:
        if category == 'nappies':
            return 'Nappy'
        if category == 'expressed':
            return f'Expressing'
        if category == 'str':
            return 'Sleep training'
        else:
            return category.capitalize()
