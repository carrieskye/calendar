import json
from datetime import datetime, time, date

import jsonpickle
import pytz
from dateutil.relativedelta import relativedelta
from skye_comlib.utils.file import File
from skye_comlib.utils.input import Input
from skye_comlib.utils.logger import Logger

from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Data, GeoLocations
from src.models.activity import Activity, Activities
from src.models.calendar import Owner
from src.models.event import Event
from src.scripts.activity.activity import ActivityScript


class UpdateCalendar(ActivityScript):
    def __init__(self):
        super().__init__()

        self.owner = self.get_owner(default=Owner.carrie)
        start = Input.get_date_input("Start")
        # end = Input.get_date_input("End")
        days = Input.get_int_input("Days", "#days")
        self.location = self.get_location()

        # TODO find cleaner way later
        self.start = self.correct_time_offset(start)
        # self.end = self.correct_time_offset(end)
        self.end = self.start + relativedelta(days=days)
        self.work_from_home = Input.get_bool_input("Work from home", default="y")

    def correct_time_offset(self, original: date):
        original_date_time = datetime.combine(original, time(5, 0))
        date_time_with_tz = original_date_time.astimezone(
            pytz.timezone(self.location.time_zone)
        )
        offset = int(str(date_time_with_tz)[-5:-3])
        return original_date_time - relativedelta(hours=offset)

    def run(self):
        Logger.sub_title("Processing")

        day = self.start
        while day < self.end:
            try:
                file_name = (
                    f"data/activity/{self.owner.name}/json/%s.json"
                    % day.strftime("%Y-%m-%d")
                )
                Logger.bold(day.strftime("%Y-%m-%d"))
                activities = jsonpickle.decode(json.dumps(File.read_json(file_name)))

                self.remove_events(day)
                self.create_events(activities)

            except FileNotFoundError:
                pass

            day += relativedelta(days=1)
            Logger.empty_line()

    def remove_events(self, day: datetime):
        for calendar in Data.calendar_dict.values():
            for owner in [self.owner, Owner.shared]:
                if not calendar.get_cal_id(owner):
                    continue

                events = GoogleCalAPI.get_events(
                    calendar, owner, 1000, day, day + relativedelta(days=1)
                )
                for event in events:
                    event_day = event.start.date_time - relativedelta(hours=4)
                    if event_day.day == day.day:
                        GoogleCalAPI.delete_event(
                            calendar.get_cal_id(owner), event.event_id
                        )

    def create_events(self, activities: Activities):
        for activity in activities:
            Logger.log(activity.__str__())
            cal_id = activity.calendar.get_cal_id(activity.owner)
            if activity.sub_activities:
                sub_activities = "\n".join(
                    [x.__str__() for x in activity.sub_activities]
                )
                self.create_event(cal_id, activity, activity.title, sub_activities)
            else:
                self.create_event(cal_id, activity, activity.title)

    def create_event(
        self, cal_id: str, activity: Activity, summary: str, description: str = ""
    ):
        if (
            summary in ["Amplyfi", "Lunch"]
            and not self.work_from_home
            and not activity.location
        ):
            location = GeoLocations.tramshed_tech.short
        else:
            if activity.trajectory:
                start_loc, end_loc = activity.trajectory.split(" > ")
                location = f"{Data.geo_location_dict[start_loc].short} > {Data.geo_location_dict[end_loc].short}"
            else:
                location = (
                    activity.location.short
                    if activity.location
                    else self.location.short
                )
        event = Event(
            summary=summary,
            location=location,
            description=description,
            start=activity.start,
            end=activity.end,
        )
        GoogleCalAPI.create_event(cal_id, event)
