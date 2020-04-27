from __future__ import annotations

import json
from datetime import timedelta
from typing import List

from dateutil.parser import parse

from src.data.data import Data
from src.models.calendar import Calendar, Owner
from src.models.event_datetime import EventDateTime
from src.models.geo_location import GeoLocation


class SubActivity:

    def __init__(self, activity_id: int, title: str, project: str, start: EventDateTime, end: EventDateTime):
        self.activity_id = activity_id
        self.title = title
        self.project = project
        self.start = start
        self.end = end

    def __str__(self) -> str:
        period = f'%s - %s' % (self.start.date_time.strftime('%H:%M:%S'), self.end.date_time.strftime('%H:%M:%S'))
        title = f'{self.project} ▸ {self.title}' if self.project else self.title
        return f'{period}: {title}'


class Activity(SubActivity):

    def __init__(self, activity_id: int, title: str, start: EventDateTime, end: EventDateTime, calendar: Calendar,
                 owner: Owner, location: GeoLocation, project: str = '', sub_activities: List[SubActivity] = []):
        super().__init__(activity_id, title, project, start, end)
        self.calendar = calendar
        self.owner = owner
        self.location = location
        self.sub_activities = sub_activities

    def __str__(self) -> str:
        result = f'{self.title} ({self.calendar.name}): %s - %s' \
                 % (self.start.date_time.strftime('%H:%M:%S'), self.end.date_time.strftime('%H:%M:%S'))
        for sub_activity in self.sub_activities:
            result += f'\n  - {sub_activity.__str__()}'
        return result

    def flatten(self) -> dict:
        return {
            'start': self.start.date_time.__str__(),
            'end': self.end.date_time.__str__(),
            'title': self.title,
            'calendar': self.calendar.name,
            'owner': self.owner.name,
            'location': self.location.address if self.location else '',
            'details': [x.__str__() for x in self.sub_activities]
        }

    def get_duration(self) -> timedelta:
        return self.end.date_time - self.start.date_time

    @classmethod
    def from_dict(cls, original: dict, time_zone: str, owner: Owner) -> Activity:
        activity_id = original['ID']
        start = EventDateTime(parse(original['Start Date']), time_zone)
        end = EventDateTime(parse(original['End Date']), time_zone)
        calendar = Data.calendar_dict[original['Project'].split(' ▸ ')[0].lower()]
        notes = json.loads(original['Notes']) if original['Notes'] else {}
        owner = Owner.shared if notes.get('shared', False) else owner
        location = Data.geo_location_dict[notes['location']] if 'location' in notes else None

        title, sub_activities, project = original['Title'], [], ''

        if calendar.name in ['projects', 'work', 'leisure']:
            if calendar.name == 'work':
                project = original['Project'].split(' ▸ ')[-1]

            if calendar.name == 'leisure':
                title = 'TV'
                url = notes['url']
                project = original['Title']
                detail = notes['episode'] if 'episode' in notes else notes['year']
                sub_activities = [SubActivity(activity_id, f'<a href="{url}">{project} {detail}</a>', '', start, end)]
                owner = Owner.shared

            else:
                title = original['Project'].split(' ▸ ')[1]
                sub_activities = [SubActivity(activity_id, original['Title'], project, start, end)]

        return cls(activity_id, title, start, end, calendar, owner, location, project, sub_activities)


class Activities(List[Activity]):

    def sort_chronically(self):
        self.sort(key=lambda x: x.start.__str__())

    def merge_short_activities(self, max_time_diff: timedelta = timedelta(minutes=20)):
        self.sort_chronically()

        work_activities = Activities([x for x in self if x.calendar.name == 'work'])
        project_activities = Activities([x for x in self if x.calendar.name == 'projects'])
        leisure_activities = Activities([x for x in self if x.calendar.name == 'leisure'])
        for activity in work_activities + project_activities + leisure_activities:
            self.remove(activity)

        for activities_to_merge in [work_activities, project_activities, leisure_activities]:
            to_merge = []
            for index, activity in enumerate(activities_to_merge[:-1]):
                next_activity = activities_to_merge[index + 1]
                time_diff = next_activity.start.date_time - activity.end.date_time
                if time_diff <= max_time_diff:
                    to_merge.append(index)

            for index in sorted(to_merge, reverse=True):
                activities_to_merge.merge(index)

            for activity in activities_to_merge:
                self.append(activity)

        self.sort_chronically()

    def merge(self, index: int):
        next_activity = self.pop(index + 1)
        activity = self.pop(index)

        longest_activity = max([activity, next_activity],
                               key=lambda x: (x.project not in ['General', 'ML'], x.get_duration()))

        longest_activity.sub_activities = activity.sub_activities + next_activity.sub_activities
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
                # If the next activity starts more than 30 minutes after this activity, continue
                if self[index + 1].start.date_time >= activity.start.date_time + timedelta(minutes=30):
                    continue
                # If there is no previous activity or the previous activity is more than 30 minutes before this one,
                # move the start of the activity up to make the length of the activity 30 minutes
                elif index == 0 or self[index - 1].end.date_time <= activity.end.date_time - timedelta(minutes=30):
                    activity.start.date_time = activity.end.date_time - timedelta(minutes=30)
                # If the next activity is also shorter than 30 minutes and the activity after that is the same as this
                # activity, merge the same activities
                elif self[index + 1].get_duration() < timedelta(minutes=30) and len(
                        self) > index + 2 and activity.calendar == self[index + 2].calendar:
                    self.remove(activity)
                    self[index].start = self[index - 1].end
                else:
                    activity.start.date_time = self[index - 1].end.date_time
                    activity.end.date_time = activity.start.date_time + timedelta(minutes=30)
                    self[index + 1].start.date_time = activity.end.date_time

        self.merge_short_activities()
