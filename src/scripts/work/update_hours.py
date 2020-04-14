from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Calendars, GeoLocations
from src.models.activity import Activity, Activities
from src.models.calendar import Owner
from src.scripts.script import Work
# from src.utils.input import Input
from src.utils.output import Output
from src.utils.utils import Utils


class UpdateHours(Work):

    def __init__(self):
        super().__init__()

        # start = Input.get_date_input('Start')
        # self.start = datetime.combine(start, time(4, 0))
        # days = Input.get_int_input('Days', '#days')
        self.start = datetime(2020, 4, 9, 4, 0)  # TODO remove
        days = 2  # TODO remove
        self.end = self.start + relativedelta(days=days)

    def run(self):
        Output.make_title('Processing')

        day = self.start
        while day < self.end:
            file_name = 'data/activity/%s.csv' % day.strftime('%Y-%m-%d')
            activities = [Activity.from_dict(x, GeoLocations.bromsgrove_st.time_zone) for x in Utils.read_csv(file_name)]
            work_activities = Activities([x for x in activities if x.category == 'Amplyfi'])
            work_activities.sort_chronically()
            work_activities.merge_short_activities(timedelta(minutes=20))

            events = GoogleCalAPI.get_events(Calendars.work, Owner.carrie, 1000, self.start,
                                             self.start + relativedelta(days=1))
            for event in events:
                print(event.serialise_for_google())
            day += relativedelta(days=1)
            print()
