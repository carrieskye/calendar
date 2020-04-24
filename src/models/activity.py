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

    def merge_short_work_activities(self, max_time_diff: timedelta = timedelta(minutes=20)):
        self.sort_chronically()

        work_activities = Activities([x for x in self if x.category == 'Amplyfi'])
        for activity in work_activities:
            self.remove(activity)

        to_merge = []
        for index, activity in enumerate(work_activities[:-1]):
            next_activity = work_activities[index + 1]
            time_diff = next_activity.start.date_time - activity.end.date_time
            if time_diff <= max_time_diff:
                to_merge.append(index)

        for index in sorted(to_merge, reverse=True):
            work_activities.merge(index)

        for work_activity in work_activities:
            self.append(work_activity)

        self.sort_chronically()

    def merge(self, index: int):
        next_activity = self.pop(index + 1)
        activity = self.pop(index)
        longest_activity = max([activity, next_activity], key=lambda x: (x.priority, x.get_duration()))

        longest_activity.start = activity.start
        longest_activity.end = next_activity.end
        self.insert(index, longest_activity)

    def remove_double_activities(self):
        self.sort_chronically()

        for index, activity in enumerate(self[1:]):
            if activity.end.date_time < self[index].end.date_time:
                self.remove(activity)

    def standardise_short_activities(self):
        for index, activity in enumerate(self):
            if activity == self[-1]:
                break
            if activity.get_duration() < timedelta(minutes=30):
                if self[index + 1].start.date_time >= activity.start.date_time + timedelta(minutes=30):
                    continue
                elif index == 0 or self[index - 1].end.date_time <= activity.end.date_time - timedelta(minutes=30):
                    activity.start.date_time = activity.end.date_time - timedelta(minutes=30)
                elif self[index + 1].get_duration() < timedelta(minutes=30) and len(
                        self) > index + 1 and activity.project == self[index + 2].project:
                    self.remove(activity)
                    self[index].start = self[index - 1].end
                else:
                    activity.start.date_time = self[index - 1].end.date_time
                    activity.end.date_time = activity.start.date_time + timedelta(minutes=30)
                    self[index + 1].start.date_time = activity.end.date_time

        self.merge_short_work_activities()
