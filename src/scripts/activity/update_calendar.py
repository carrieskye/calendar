import logging
from datetime import date, datetime, time
from pathlib import Path

import pytz  # type: ignore
from dateutil.relativedelta import relativedelta  # type: ignore
from skye_comlib.utils.file import File
from skye_comlib.utils.formatter import Formatter
from skye_comlib.utils.input import Input

from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Data, GeoLocations
from src.models.activity.activities import Activities
from src.models.activity.activity import Activity
from src.models.calendar import Owner
from src.models.event import Event
from src.scripts.activity.activity_script import ActivityScript


class UpdateCalendar(ActivityScript):
    def __init__(self) -> None:
        super().__init__()

        start = Input.get_date_input("Start")
        days = Input.get_int_input("Days", "#days")

        self.owner = Owner.carrie
        self.work_from_home = True
        self.location = Data.geo_location_dict["järnvägsgatan_41_orsa"]

        self.start = self.correct_time_offset(start)
        self.end = self.start + relativedelta(days=days)

    def correct_time_offset(self, original: date) -> datetime:
        original_date_time = datetime.combine(original, time(5))
        date_time_with_tz = original_date_time.astimezone(pytz.timezone(self.location.time_zone))
        offset = int(str(date_time_with_tz)[-5:-3])
        return original_date_time - relativedelta(hours=offset)

    def run(self) -> None:
        logging.info(Formatter.sub_title("Processing"), extra={"markup": True})

        owner_dir = Path("data/activity") / self.owner.name

        day = self.start
        while day < self.end:
            try:
                day_str = day.strftime("%Y-%m-%d")
                file_name = owner_dir / f"json/{day_str}.json"
                logging.info(f"[bold]{day_str}", extra={"markup": True})
                activities = File.read_json_pickle(file_name)

                self.remove_events(day)
                self.create_events(activities)

            except FileNotFoundError:
                pass

            day += relativedelta(days=1)

    def remove_events(self, day: datetime) -> None:
        for calendar in Data.calendar_dict.values():
            for owner in [self.owner, Owner.shared]:
                if not calendar.get_cal_id(owner):
                    continue

                events = GoogleCalAPI.get_events(calendar, owner, 1000, day, day + relativedelta(days=1))
                for event in events:
                    event_day = event.start.date_time - relativedelta(hours=4)
                    if event_day.day == day.day:
                        GoogleCalAPI.delete_event(calendar.get_cal_id(owner), event.event_id)

    def create_events(self, activities: Activities) -> None:
        for activity in activities:
            logging.info(
                f"{activity.start.date_time.strftime('%H:%M:%S')} - "
                f"{activity.end.date_time.strftime('%H:%M:%S')}: "
                f"{activity.title} ({activity.calendar.name})",
            )
            cal_id = activity.calendar.get_cal_id(activity.owner)
            if activity.sub_activities:
                sub_activities = "\n".join([x.__str__() for x in activity.sub_activities])
                self.create_event(cal_id, activity, activity.title, sub_activities)
            else:
                self.create_event(cal_id, activity, activity.title)

    def create_event(self, cal_id: str, activity: Activity, summary: str, description: str = "") -> None:
        if summary in ["Amplyfi", "Lunch"] and not self.work_from_home and not activity.location:
            location = GeoLocations.tramshed_tech.short
        else:
            if activity.trajectory:
                location = (
                    f"{Data.geo_location_dict[activity.trajectory.origin].short} > "
                    f"{Data.geo_location_dict[activity.trajectory.destination].short}"
                )
            else:
                location = activity.location.short if activity.location else self.location.short
        event = Event(
            summary=summary,
            location=location,
            description=description,
            start=activity.start,
            end=activity.end,
        )
        GoogleCalAPI.create_event(cal_id, event)
