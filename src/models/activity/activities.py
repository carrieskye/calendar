from collections import defaultdict
from datetime import timedelta
from pathlib import Path

from pytz import timezone

from src.utils import File

from ..location import GeoLocation
from .activity import Activity


class Activities(list[Activity]):
    @classmethod
    def read_json_file(cls, path: Path) -> "Activities":
        raw = File.read_json(path)
        if raw is None:
            return cls()
        if not isinstance(raw, list):
            raise ValueError(f"Expected a JSON array in {path}, got {type(raw).__name__}")
        return cls(Activity.model_validate(item) for item in raw)

    def write_json_file(self, path: Path) -> None:
        File.write_json([activity.model_dump(mode="json") for activity in self], path)

    def sort_chronically(self) -> None:
        self.sort(key=lambda x: x.start.date_time.astimezone(timezone("UTC")))

    def merge_short_activities(self, max_time_diff: timedelta, default_location: GeoLocation) -> None:
        self.sort_chronically()

        activity_groups: dict[str, Activities] = defaultdict(Activities)
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
                if activity.location and next_activity.location and activity.location != next_activity.location:
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

    def merge(self, index: int) -> None:
        # TODO: if there are multiple locations, keep the most frequent one when merging
        next_activity = self.pop(index + 1)
        activity = self.pop(index)

        longest_activity = max([activity, next_activity], key=lambda x: (x.location is not None, x.duration))

        longest_activity.sub_activities = activity.sub_activities + next_activity.sub_activities
        longest_activity.start = activity.start
        longest_activity.end = next_activity.end
        self.insert(index, longest_activity)

    def remove_double_activities(self) -> None:
        self.sort_chronically()

        for index, activity in enumerate(self):
            if index == 0:
                continue
            if activity.end.date_time < self[index - 1].end.date_time:
                self.remove(activity)
