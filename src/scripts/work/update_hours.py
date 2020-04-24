from datetime import datetime, timedelta, time

from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Calendars
from src.models.activity import Activity, Activities
from src.models.calendar import Owner
from src.models.event import Event
from src.scripts.script import Work
from src.utils.input import Input
from src.utils.output import Output
from src.utils.utils import Utils

CALENDAR_LOOKUP = {
    'Activity': Calendars.projects,
    'Photos': Calendars.projects,
    'Groceries': Calendars.various,
    'Social': Calendars.friends_and_family,
    'Food': Calendars.food,
    'Sports': Calendars.sports,
    'Work': Calendars.work,
    'Duolingo': Calendars.school,
    'Jobs': Calendars.various,
    'Medical': Calendars.medical
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

    def run(self):
        Output.make_title('Processing')

        day = self.start
        while day < self.end:
            file_name = f'data/activity/{self.owner.name}/%s.csv' % day.strftime('%Y-%m-%d')
            activities = Activities([Activity.from_dict(x, self.location.time_zone) for x in Utils.read_csv(file_name)])
            activities.merge_short_work_activities(timedelta(minutes=20))
            activities.remove_double_activities()
            activities.standardise_short_activities()

            for calendar in CALENDAR_LOOKUP.values():
                events = GoogleCalAPI.get_events(calendar, self.owner, 1000, day, day + relativedelta(days=1))
                for event in events:
                    GoogleCalAPI.delete_event(calendar.get_cal_id(self.owner), event.event_id)

            for activity in activities:
                if activity.category == 'Amplyfi':
                    self.create_work_event(activity)
                else:
                    self.create_other_event(activity)

            day += relativedelta(days=1)

    def create_work_event(self, activity: Activity):
        self.create_event(Calendars.work.get_cal_id(self.owner), activity, 'Amplyfi', activity.project)

    def create_other_event(self, activity: Activity):
        if activity.project in CALENDAR_LOOKUP:
            calendar = CALENDAR_LOOKUP[activity.project]
            if calendar in SHARED_ACTIVITIES:
                self.create_event(calendar.get_cal_id(Owner.shared), activity, activity.title)
            else:
                self.create_event(CALENDAR_LOOKUP[activity.project].get_cal_id(self.owner), activity, activity.title)
        else:
            self.create_event(Calendars.various.get_cal_id(Owner.shared), activity, activity.title)

    def create_event(self, cal_id: str, activity: Activity, summary: str, description: str = ''):
        event = Event(
            summary=summary,
            location=self.location.address.__str__(),
            description=description,
            start=activity.start,
            end=activity.end
        )
        GoogleCalAPI.create_event(cal_id, event)
