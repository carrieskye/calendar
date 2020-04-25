from datetime import datetime, timedelta, time

from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Calendars, Data
from src.models.activity import Activity, Activities, WorkActivity
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

    def run(self):
        Output.make_title('Processing')

        day = self.start
        while day < self.end:
            file_name = f'data/activity/{self.owner.name}/%s.csv' % day.strftime('%Y-%m-%d')
            activities = Activities.from_dict(Utils.read_csv(file_name), self.location.time_zone)
            activities.merge_short_work_activities(timedelta(minutes=20))
            activities.remove_double_activities()
            activities.standardise_short_activities()

            self.remove_events(day)
            self.create_events(activities)

            day += relativedelta(days=1)

    def remove_events(self, day: datetime):
        for calendar in Data.calendar_dict.values():
            if calendar == Calendars.leisure:
                continue

            for owner in [self.owner, Owner.shared]:
                if not calendar.get_cal_id(owner):
                    continue

                events = GoogleCalAPI.get_events(calendar, owner, 1000, day, day + relativedelta(days=1))
                for event in events:
                    GoogleCalAPI.delete_event(calendar.get_cal_id(owner), event.event_id)

    def create_events(self, activities: Activities):
        for activity in activities:
            Utils.log(activity.__str__())
            if isinstance(activity, WorkActivity):
                self.create_event(Calendars.work.get_cal_id(self.owner), activity, activity.company, activity.project)
            else:
                if activity.calendar in SHARED_ACTIVITIES:
                    self.create_event(activity.calendar.get_cal_id(Owner.shared), activity, activity.title)
                else:
                    self.create_event(activity.calendar.get_cal_id(self.owner), activity, activity.title)

    def create_event(self, cal_id: str, activity: Activity, summary: str, description: str = ''):
        event = Event(
            summary=summary,
            location=self.location.address.__str__(),
            description=description,
            start=activity.start,
            end=activity.end
        )
        GoogleCalAPI.create_event(cal_id, event)
