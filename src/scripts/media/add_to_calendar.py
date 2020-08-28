from datetime import datetime

from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalAPI
from src.connectors.trakt import TraktAPI
from src.data.data import Calendars
from src.scripts.media.media import MediaScript
from src.utils.input import Input
from src.utils.logger import Logger


class AddToCalendar(MediaScript):

    def __init__(self, start: datetime = None, days: int = None):
        super().__init__()

        if not start:
            start = Input.get_date_input('Start')
        if not days:
            days = Input.get_int_input('Days', input_type='#days')

        self.start = start + relativedelta(hours=4)
        self.end = self.start + relativedelta(days=int(days))
        self.owner = self.get_owner()
        self.location = self.get_location()

    def run(self):
        Logger.title('Processing')

        events = GoogleCalAPI.get_events(self.calendar, self.owner, 1000, self.start, self.end)
        for event in events:
            GoogleCalAPI.delete_event(self.calendar.get_cal_id(self.owner), event.event_id)

        history = sorted(TraktAPI.get_history(self.start, self.end), key=lambda x: x.get('watched_at'))
        for watch in self.get_watches_from_history(history):
            Logger.log(watch.__str__())
            self.create_watch_event(self.calendar, self.owner, watch, self.location)
