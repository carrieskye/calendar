from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from typing import List

from dateutil.parser import parse
from pytz import timezone
from skye_comlib.utils.formatter import Formatter

from src.data.data import Data
from src.models.calendar import Calendar, Owner
from src.models.event_datetime import EventDateTime
from src.models.location.geo_location import GeoLocation


class SubActivity:
    def __init__(self, activity_id: int, projects: List[str], start: EventDateTime, end: EventDateTime):
        self.activity_id = activity_id
        self.projects = projects
        self.start = start
        self.end = end

    def __str__(self) -> str:
        self.start.correct_time_zone()
        self.end.correct_time_zone()
        period = "%s - %s" % (self.start.date_time.strftime("%H:%M:%S"), self.end.date_time.strftime("%H:%M:%S"))
        title = " ▸ ".join(self.projects)
        return f"{period}: {title}"


class Activity(SubActivity):
    projects_to_ignore = [
        "Maternity",
        "Help people",
        "Food",
        "Friends",
        "Family",
        "Home studio",
        "Travel",
        "Household"
    ]

    def __init__(
        self,
        activity_id: int,
        title: str,
        start: EventDateTime,
        end: EventDateTime,
        calendar: Calendar,
        owner: Owner,
        location: GeoLocation,
        trajectory: str,
        projects: List[str] = [],
        sub_activities: List[SubActivity] = [],
    ):
        super().__init__(activity_id, projects, start, end)
        self.title = title
        self.calendar = calendar
        self.owner = owner
        self.location = location
        self.trajectory = trajectory
        self.sub_activities = sub_activities

    def __str__(self) -> str:
        result = (
            f"{self.title} ({self.calendar.name}): "
            f"{self.start.date_time.strftime('%H:%M:%S')} - "
            f"{self.end.date_time.strftime('%H:%M:%S')}"
        )
        for sub_activity in self.sub_activities:
            result += f"\n  • {sub_activity.__str__()}"
        return result

    def flatten(self) -> dict:
        return {
            "start": self.start.date_time.__str__(),
            "end": self.end.date_time.__str__(),
            "title": self.title,
            "calendar": self.calendar.name,
            "owner": self.owner.name,
            "location": self.location.address if self.location else "",
            "trajectory": self.trajectory,
            "details": [x.__str__() for x in self.sub_activities],
        }

    def get_duration(self) -> timedelta:
        return self.end.date_time - self.start.date_time

    @classmethod
    def from_dict(cls, original: dict, time_zone: str, owner: Owner) -> Activity:
        activity_id = original["ID"]
        projects = original["Project"].split(" ▸ ") + [original["Title"]]
        calendar = Data.calendar_dict[projects.pop(0).lower()]
        notes = Formatter.de_serialise_details(original["Notes"])
        owner = Owner.shared if notes.get("shared", False) else owner
        location = Data.geo_location_dict[notes["location"]] if "location" in notes else None
        trajectory = notes["trajectory"] if "trajectory" in notes else ""
        details = notes["details"] if "details" in notes else ""

        start_time_zone = location.time_zone if location else time_zone
        end_time_zone = location.time_zone if location else time_zone

        if trajectory:
            start_location, end_location = trajectory.split(" > ")
            location = Data.geo_location_dict[start_location]
            start_time_zone = Data.geo_location_dict[start_location].time_zone
            end_time_zone = Data.geo_location_dict[end_location].time_zone

        start = EventDateTime(parse(original["Start Date"]), start_time_zone)
        end = EventDateTime(parse(original["End Date"]), end_time_zone)

        title, sub_activities = original["Title"], []
        projects = list(filter(lambda x: x != "Various", projects))

        if calendar.name == "leisure" and projects and projects[0] == "TV":
            title = "TV"
            url = notes["url"]
            name = original["Title"]
            detail = notes["episode"] if "episode" in notes else notes["year"]
            sub_activities = [SubActivity(activity_id, [f'<a href="{url}">{name} ({detail})</a>'], start, end)]

        else:
            if projects[0] in cls.projects_to_ignore:
                projects.pop(0)

            title = projects.pop(0)
            if notes.get("transport"):
                sub_activities = [SubActivity(activity_id, [notes.get("transport").capitalize()], start, end)]
            elif projects:
                sub_activities = [SubActivity(activity_id, projects, start, end)]
            elif notes.get("location"):
                sub_activities = [SubActivity(activity_id, [title] if not details else [details], start, end)]

        return cls(activity_id, title, start, end, calendar, owner, location, trajectory, projects, sub_activities)


class Activities(List[Activity]):
    def sort_chronically(self):
        self.sort(key=lambda x: x.start.date_time.astimezone(timezone("UTC")))

    def merge_short_activities(
        self, max_time_diff: timedelta = timedelta(minutes=20), default_location: GeoLocation = None
    ):
        self.sort_chronically()

        activity_groups = defaultdict(Activities)
        for x in self:
            activity_groups[x.title].append(x)

        for group in activity_groups.values():
            for activity in group:
                self.remove(activity)

        for activities_to_merge in activity_groups.values():
            to_merge = []
            for index, activity in enumerate(activities_to_merge[:-1]):
                next_activity = activities_to_merge[index + 1]
                time_diff = next_activity.start.date_time - activity.end.date_time
                if time_diff > max_time_diff:
                    continue
                if activity.owner != next_activity.owner:
                    continue
                if activity.calendar != next_activity.calendar:
                    continue
                if activity.location and next_activity.location:
                    if activity.location != next_activity.location:
                        continue
                to_merge.append(index)

            for index in sorted(to_merge, reverse=True):
                activities_to_merge.merge(index)

            for activity in activities_to_merge:
                self.append(activity)

        for activity in self:
            location = activity.location if activity.location else default_location
            activity.start.time_zone = location.time_zone
            activity.end.time_zone = location.time_zone
            activity.start.correct_time_zone()
            activity.end.correct_time_zone()
            for sub_activity in activity.sub_activities:
                sub_activity.start.time_zone = location.time_zone
                sub_activity.end.time_zone = location.time_zone
                sub_activity.start.correct_time_zone()
                sub_activity.end.correct_time_zone()

        self.sort_chronically()

    def merge(self, index: int):
        # TODO: if there are multiple locations, keep the most frequent one when merging
        next_activity = self.pop(index + 1)
        activity = self.pop(index)

        longest_activity = max(
            [activity, next_activity],
            key=lambda x: (x.location is not None, x.get_duration()),
        )

        longest_activity.sub_activities = activity.sub_activities + next_activity.sub_activities
        longest_activity.start = activity.start
        longest_activity.end = next_activity.end
        self.insert(index, longest_activity)

    def remove_double_activities(self):
        self.sort_chronically()

        for index, activity in enumerate(self):
            if index == 0:
                continue
            if activity.end.date_time < self[index - 1].end.date_time:
                self.remove(activity)
