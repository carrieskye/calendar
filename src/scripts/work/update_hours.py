import json
from datetime import datetime, time

import jsonpickle
from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Calendars, Data, GeoLocations
from src.models.activity import Activity, Activities
from src.models.calendar import Owner
from src.models.event import Event
from src.scripts.script import Work
from src.utils.input import Input
from src.utils.output import Output
from src.utils.utils import Utils

CALENDAR_LOOKUP = {
    'Projects': Calendars.projects,
    'Social': Calendars.social,
    'Food': Calendars.food,
    'Sports': Calendars.sports,
    'Medical': Calendars.medical,
    'Work': Calendars.work
}

SHARED_ACTIVITIES = [Calendars.medical, Calendars.sports]


class UpdateHours(Work):

    def __init__(self):
        super().__init__()

        start = Input.get_date_input('Start')
        days = Input.get_int_input('Days', '#days')

        self.start = datetime.combine(start, time(4, 0))
        self.end = self.start + relativedelta(days=days)
        self.location = self.get_location()
        self.owner = self.get_owner(default=Owner.carrie)
        self.work_from_home = Input.get_bool_input('Work from home', default='y')

    def run(self):
        Output.make_title('Processing')

        day = self.start
        while day < self.end:
            try:
                file_name = f'data/activity/{self.owner.name}/json/%s.json' % day.strftime('%Y-%m-%d')
                Output.make_bold(day.strftime('%Y-%m-%d'))
                activities = jsonpickle.decode(json.dumps(Utils.read_json(file_name)))

                self.remove_events(day)
                self.create_events(activities)

            except FileNotFoundError:
                pass

            day += relativedelta(days=1)
            Utils.log('')

    def remove_events(self, day: datetime):
        for calendar in Data.calendar_dict.values():
            for owner in [self.owner, Owner.shared]:
                if not calendar.get_cal_id(owner):
                    continue

                events = GoogleCalAPI.get_events(calendar, owner, 1000, day, day + relativedelta(days=1))
                for event in events:
                    GoogleCalAPI.delete_event(calendar.get_cal_id(owner), event.event_id)

    def create_events(self, activities: Activities):
        for activity in activities:
            Utils.log(activity.__str__())
            cal_id = activity.calendar.get_cal_id(activity.owner)
            if activity.sub_activities:
                sub_activities = '\n'.join([x.__str__() for x in activity.sub_activities])
                self.create_event(cal_id, activity, activity.title, sub_activities)
            else:
                self.create_event(cal_id, activity, activity.title)

    def create_event(self, cal_id: str, activity: Activity, summary: str, description: str = ''):
        if summary in ['Amplyfi', 'Lunch'] and not self.work_from_home:
            location = GeoLocations.tramshed_tech
        else:
            location = activity.location if activity.location else self.location
        event = Event(
            summary=summary,
            location=location.address.__str__(),
            description=description,
            start=activity.start,
            end=activity.end
        )
        GoogleCalAPI.create_event(cal_id, event)
