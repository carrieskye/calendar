from datetime import datetime, time, timedelta

from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Calendars
from src.models.activity import Activity, Activities
from src.scripts.script import Work
from src.utils.input import Input
from src.utils.output import Output
from src.utils.utils import Utils


class UpdateHours(Work):

    def __init__(self):
        super().__init__()

        start = Input.get_date_input('Start')
        self.start = datetime.combine(start, time(4, 0))
        self.start -= relativedelta(days=3)  # TODO remove
        # days = Input.get_int_input('Days', '#days')
        days = 2  # TODO remove
        self.end = self.start + relativedelta(days=days)

    def run(self):
        Output.make_title('Processing')

        day = self.start
        while day < self.end:
            file_name = 'data/activity/%s.csv' % day.strftime('%Y-%m-%d')
            activities = [Activity.from_dict(x, self.time_zone) for x in Utils.read_csv(file_name)]
            work_activities = Activities([x for x in activities if x.category == 'Amplyfi'])
            work_activities.sort_chronically()
            work_activities.merge_short_activities(timedelta(minutes=20))

            events = GoogleCalAPI.get_events(Calendars.work.carrie, 1000, self.start,
                                             self.start + relativedelta(days=1))
            for event in events:
                print(event)
            day += relativedelta(days=1)
            print()
