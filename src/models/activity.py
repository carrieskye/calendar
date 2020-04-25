from __future__ import annotations

from datetime import timedelta
from typing import List

from dateutil.parser import parse

from src.data.data import Data
from src.models.calendar import Calendar
from src.models.event_datetime import EventDateTime


class Activity:

    def __init__(self, original: dict, time_zone: str):
        self.activity_id = original['ID']
        self.calendar: Calendar = Data.calendar_dict[original['Project'].split(' ▸ ')[0].lower()]
        self.title = original['Title']
        self.start = EventDateTime(parse(original['Start Date']), time_zone)
        self.end = EventDateTime(parse(original['End Date']), time_zone)

    def __str__(self) -> str:
        return f'{self.title} ({self.calendar.name}): %s - %s' \
               % (self.start.date_time.strftime('%H:%M:%S'), self.end.date_time.strftime('%H:%M:%S'))

    def get_duration(self) -> timedelta:
        return self.end.date_time - self.start.date_time


class WorkActivity(Activity):

    def __init__(self, original: dict, time_zone: str):
        self.company, self.project = original['Project'].split(' ▸ ')[1:]
        self.priority = 1 if self.project not in ['General', 'ML'] else 0
        super().__init__(original, time_zone)

    def __str__(self) -> str:
        return f'{self.title} ({self.calendar.name} ▸ {self.company} ▸ {self.project}): %s - %s' \
               % (self.start.date_time.strftime('%H:%M:%S'), self.end.date_time.strftime('%H:%M:%S'))


class Activities(List[Activity]):

    @classmethod
    def from_dict(cls, export: List[dict], time_zone: str) -> Activities:
        activities = cls()
        for original in export:
            calendar = original['Project'].split(' ▸ ')[0]
            if calendar == 'Work':
                activities.append(WorkActivity(original, time_zone))
            elif calendar != 'Streaming':
                activities.append(Activity(original, time_zone))

        return activities

    def sort_chronically(self):
        self.sort(key=lambda x: x.start.__str__())

    def merge_short_work_activities(self, max_time_diff: timedelta = timedelta(minutes=20)):
        self.sort_chronically()

        work_activities = Activities([x for x in self if isinstance(x, WorkActivity)])
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
                        self) > index + 1 and activity.calendar == self[index + 2].calendar:
                    self.remove(activity)
                    self[index].start = self[index - 1].end
                else:
                    activity.start.date_time = self[index - 1].end.date_time
                    activity.end.date_time = activity.start.date_time + timedelta(minutes=30)
                    self[index + 1].start.date_time = activity.end.date_time

        self.merge_short_work_activities()
