from __future__ import annotations

from datetime import timedelta
from typing import List

from dateutil.parser import parse

from src.models.event_datetime import EventDateTime


class Activity:

    def __init__(self, category: str, project: str, title: str, start: EventDateTime, end: EventDateTime):
        self.category = category
        self.project = project
        self.title = title
        self.start = start
        self.end = end
        self.priority = 1 if project not in ['General', 'ML'] else 0

    def __str__(self):
        return f'{self.title} ({self.project}, {self.category}): %s - %s' \
               % (self.start.date_time.strftime('%H:%M:%S'), self.end.date_time.strftime('%H:%M:%S'))

    def get_duration(self) -> timedelta:
        return self.end.date_time - self.start.date_time

    @classmethod
    def from_dict(cls, original: dict, time_zone: str) -> Activity:
        return cls(
            category=original['Top-Level Project'],
            project=original['Second-Level Project'],
            title=original['Title'],
            start=EventDateTime(parse(original['Start Date']), time_zone),
            end=EventDateTime(parse(original['End Date']), time_zone)
        )


class Activities(List[Activity]):

    def sort_chronically(self):
        self.sort(key=lambda x: x.start.__str__())

    def merge_short_activities(self, max_time_diff: timedelta):
        to_merge = []
        for index, activity in enumerate(self[:-1]):
            next_activity = self[index + 1]
            time_diff = next_activity.start.date_time - activity.end.date_time
            if time_diff <= max_time_diff:
                to_merge.append(index)

        for index in sorted(to_merge, reverse=True):
            self.merge(index)

    def merge(self, index: int):
        next_activity = self.pop(index + 1)
        activity = self.pop(index)
        longest_activity = max([activity, next_activity], key=lambda x: (x.priority, x.get_duration()))

        longest_activity.start = activity.start
        longest_activity.end = next_activity.end
        self.insert(index, longest_activity)
