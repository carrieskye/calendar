from datetime import timedelta

from ..calendar import Calendar, Owner
from ..event_datetime import EventDateTime
from ..location import GeoLocation
from ..timing import TimingItem, TimingTrajectory
from .sub_activity import SubActivity


class Activity(SubActivity):
    title: str
    calendar: Calendar
    owner: Owner
    location: GeoLocation | None
    trajectory: TimingTrajectory | None
    sub_activities: list[SubActivity]

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

    @property
    def duration(self) -> timedelta:
        return self.end.date_time - self.start.date_time

    @classmethod
    def from_timing_item(cls, timing_item: TimingItem, default_location: GeoLocation, owner: Owner) -> "Activity":
        location = timing_item.get_location() or default_location
        start = EventDateTime(date_time=timing_item.start_date, time_zone=location.time_zone)
        end = EventDateTime(date_time=timing_item.end_date, time_zone=location.time_zone)
        sub_activity = cls.get_sub_activity(timing_item, start, end)
        return cls(
            activity_id=timing_item.id,
            projects=timing_item.projects,
            start=start,
            end=end,
            title=timing_item.title,
            calendar=timing_item.calendar,
            owner=owner,
            location=timing_item.get_location(),
            trajectory=timing_item.notes.trajectory,
            sub_activities=[sub_activity] if sub_activity else [],
        )

    @staticmethod
    def get_sub_activity(timing_item: TimingItem, start: EventDateTime, end: EventDateTime) -> SubActivity | None:
        if timing_item.calendar.name == "lazing" and timing_item.projects and timing_item.all_projects[1] == "TV":
            url = timing_item.notes.url
            name = timing_item.projects[-1]
            detail = timing_item.notes.episode if timing_item.notes.episode else timing_item.notes.year
            return SubActivity(
                activity_id=timing_item.id,
                projects=[f'<a href="{url}">{name} ({detail})</a>'],
                start=start,
                end=end,
            )

        title = timing_item.projects[0]
        if timing_item.notes.transport:
            return SubActivity(
                activity_id=timing_item.id,
                projects=[timing_item.notes.transport.name.capitalize()],
                start=start,
                end=end,
            )
        if len(timing_item.projects) > 1 or (
            len(timing_item.projects) == 1 and timing_item.projects[0] != timing_item.title
        ):
            return SubActivity(activity_id=timing_item.id, projects=timing_item.projects, start=start, end=end)
        if timing_item.notes.location:
            return SubActivity(
                activity_id=timing_item.id,
                projects=[title] if not timing_item.notes.details else [timing_item.notes.details],
                start=start,
                end=end,
            )
        return None
