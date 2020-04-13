from datetime import datetime, time

from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Calendars
from src.models.event import Event
from src.scripts.script import Work
from src.utils.input import Input
from src.utils.output import Output


class UpdateProject(Work):

    def __init__(self):
        super(UpdateProject, self).__init__()

        self.start = Input.get_date_input('Start')
        days = Input.get_int_input('Days', '#days')
        self.end = self.start + relativedelta(days=days)
        self.project = Input.get_string_input('Project', 'CSET')

    def run(self):
        Output.make_title('Processing')

        results = GoogleCalAPI.get_events(Calendars.work.carrie, 1000, self.start, self.end)
        for result in results:
            event = Event.from_dict(original=result, calendar=Calendars.work, owner='carrie')
            event.summary = 'Amplyfi'
            event.description = self.project
            GoogleCalAPI.update_event(Calendars.work.carrie, event.event_id, event)

        Output.make_bold('Updated work project\n')


class CopyToLarry(Work):

    def __init__(self):
        super(CopyToLarry, self).__init__()

        start = Input.get_date_input('Start')
        self.start = datetime.combine(start, time(4, 0))
        days = Input.get_int_input('Days', '#days')
        self.end = self.start + relativedelta(days=days)

    def run(self):
        Output.make_title('Processing')

        results = GoogleCalAPI.get_events(Calendars.work.larry, 1000, self.start, self.end)
        for result in results:
            event = Event.from_dict(original=result, calendar=Calendars.work.larry)
            GoogleCalAPI.delete_event(Calendars.work.larry, event.event_id)

        results = GoogleCalAPI.get_events(Calendars.work.carrie, 1000, self.start, self.end)
        for result in results:
            event = Event.from_dict(original=result, calendar=Calendars.work.carrie)
            event.summary = 'Amplyfi'
            event.location = '25 Bromsgrove St, Cardiff CF11 7EZ, UK'
            event.description = ''
            GoogleCalAPI.create_event(Calendars.work.larry, event)

        Output.make_bold('Copied to Larry\n')
