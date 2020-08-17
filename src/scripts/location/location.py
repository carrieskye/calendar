from abc import ABC
from datetime import datetime, time, date, timedelta
from math import radians, sin, atan2, sqrt, cos
from typing import List

import psycopg2
import pytz
from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Data, Calendars
from src.models.calendar import Owner
from src.models.event import Event
from src.models.event_datetime import EventDateTime
from src.models.location_event import LocationEvent
from src.models.location_event_temp import LocationEventTemp
from src.models.point import Point
from src.scripts.script import Script
from src.utils.table_print import TablePrint


class LocationScript(Script, ABC):

    @classmethod
    def get_records(cls, start: datetime, end: datetime, owner: Owner, accuracy: int = 20) -> List[tuple]:
        user_id = 3 if owner == Owner.carrie else 2
        conditions = 'WHERE ' + ' AND '.join([
            f'time > \'{start.strftime("%Y-%m-%d %H:%M:%S")}\'',
            f'time < \'{end.strftime("%Y-%m-%d %H:%M:%S")}\'',
            f'user_id = {user_id}',
            f'accuracy < {accuracy}'
        ])
        query = f'SELECT * FROM public.positions {conditions}'

        conn = psycopg2.connect(host='nuc', database='ulogger', user='postgres', password='catsies')
        cur = conn.cursor()
        cur.execute(query)
        records = cur.fetchall()
        conn.close()
        return records

    @classmethod
    def group_events(cls, events: List[LocationEventTemp]) -> List[LocationEventTemp]:
        grouped_events = []
        index = 0

        while index < len(events):
            event = events[index]

            if len(event.events) < 3 and grouped_events:
                previous = grouped_events[-1]
                same_name = previous.name == events[index + 1].name
                short_event = previous.end + relativedelta(minutes=30) > events[index + 1].start
                if same_name and short_event:
                    grouped_events.remove(previous)
                    group = LocationEventTemp(
                        name=previous.name,
                        events=previous.events + event.events + events[index + 1].events,
                        start=previous.start,
                        end=events[index + 1].end)
                    grouped_events.append(group)
                    index += 1
                else:
                    grouped_events.append(event)
            else:
                grouped_events.append(event)
            index += 1

        cls.print_events('Grouped events', grouped_events)
        return cls.merge_events(grouped_events)

    @classmethod
    def merge_events(cls, events: List[LocationEventTemp]) -> List[LocationEventTemp]:
        merged_events = []
        index = 0

        merge_start = 0

        work_day = cls.is_work_day(events)
        if not work_day:
            while index < len(events):
                event = events[index]

                if event.start + relativedelta(minutes=5) > event.end:
                    if not merge_start:
                        merge_start = index

                else:
                    if merge_start:
                        if events[merge_start - 1].name == event.name:
                            event.start = events[merge_start - 1].start
                            merged_events.pop(-1)
                        else:
                            event.start = events[merge_start].start
                    merged_events.append(event)
                    merge_start = 0

                index += 1
        else:
            merged_events = events

        cls.print_events('Merged events', merged_events)
        return cls.clean_work(merged_events)

    @classmethod
    def clean_work(cls, events: List[LocationEventTemp]) -> List[LocationEventTemp]:
        # TODO location for comparison should not be strings
        cleaned_events = []
        index = 0

        work_day = cls.is_work_day(events)
        if work_day:
            while index < len(events):
                event = events[index]

                morning = event.start.time() < time(12)
                noon = event.start.time() > time(12) and time(4) < event.end.time() < time(14, 30)
                afternoon = event.end.time() > time(14, 30)

                short_event = event.start + relativedelta(minutes=30) > event.end

                if event.name == 'tramshed_tech' and (morning or afternoon):
                    name = event.name
                    start = event.start
                    end = event.end
                    event_list = event.events
                    if events[index + 1].name == 'Amplyfi':
                        name = events[index + 1].name
                        end = events[index + 1].end
                        event_list += events[index + 1].events
                        index += 1
                    if cleaned_events[-1].name == 'Amplyfi':
                        previous = cleaned_events.pop(-1)
                        name = previous.name
                        start = previous.start
                        event_list = previous.events + event_list
                    cleaned_events.append(LocationEventTemp(name, event_list, start, end))
                elif event.name == 'Amplyfi' and noon and short_event:
                    name = event.name
                    start = event.start
                    end = event.end
                    event_list = event.events
                    if events[index + 1].name == 'tramshed_tech':
                        name = events[index + 1].name
                        end = events[index + 1].end
                        event_list += events[index + 1].events
                        index += 1
                    if cleaned_events[-1].name == 'Tramshed Tech':
                        previous = cleaned_events.pop(-1)
                        name = previous.name
                        start = previous.start
                        event_list = previous.events + event_list
                    cleaned_events.append(LocationEventTemp(name, event_list, start, end))
                elif work_day and index < len(events) - 1 and event.name != 'Amplyfi' and noon \
                        and events[index + 1].name == 'Amplyfi':
                    first_index = len(cleaned_events)
                    while first_index > 1 and cleaned_events[first_index - 1].name != 'Amplyfi':
                        first_index -= 1
                    if first_index < len(cleaned_events):
                        start = cleaned_events[first_index].start
                    else:
                        start = event.start
                    event_list = []
                    for x in range(len(cleaned_events) - 1, first_index - 1, -1):
                        event_list += cleaned_events.pop(x).events
                    event_list += event.events
                    if start + relativedelta(minutes=30) > event.end:
                        event.end = start + relativedelta(minutes=30)
                        events[index + 1].start = event.end
                    cleaned_events.append(LocationEventTemp('Tramshed Tech', event_list, start, event.end))

                else:
                    cleaned_events.append(event)
                index += 1

            cls.print_events('Cleaned work events', cleaned_events)
        else:
            cleaned_events = events

        return cleaned_events

    @classmethod
    def get_closest_location(cls, location: LocationEvent) -> str:
        matches = []
        geo_locations = cls.filter_geo_locations(location)
        for label, geo_location in geo_locations.items():
            if geo_location.within_bounding_box(location):
                matches.append(label)
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            distances = {}
            for match in matches:
                intersection = Data.geo_location_dict[match].bounding_box.intersection
                distances[match] = cls.get_distance(location.get_point(), intersection)
            match = min(distances.items(), key=lambda x: x[1])
            return match[0]

    @classmethod
    def process_events(cls, start: date, history: List[LocationEventTemp], larry: bool):
        # TODO fix
        events = GoogleCalAPI.get_all_events_for_day(start)

        table_print = TablePrint('Updated events', ['START', 'END', 'SUMMARY'], [10, 10, 30])
        for event in events:
            popped_event = cls.get_closest_event(event, history)
            if popped_event:
                start = popped_event.start.strftime('%H:%M:%S')
                end = popped_event.end.strftime('%H:%M:%S')
                table_print.print_line([start, end, event.summary])
                if event.calendar != 'work' or not larry:
                    history.pop(history.index(popped_event))
            else:
                table_print.print_line(['?', '?', event.summary])

        table_print = TablePrint('New events', ['START', 'END', 'LOCATION'], [10, 10, 30])
        for remaining_entry in history:
            unknown = remaining_entry.name == 'unknown'
            too_short = remaining_entry.start + relativedelta(minutes=30) >= remaining_entry.end
            category = Data.geo_location_dict[remaining_entry.name].category if not unknown else 'unknown'
            home = category == 'Home'
            if not (too_short or home):
                start = remaining_entry.start.strftime('%H:%M:%S')
                end = remaining_entry.end.strftime('%H:%M:%S')
                table_print.print_line([start, end, remaining_entry.name])
                if not unknown:
                    event = cls.create_default_event(remaining_entry)
                    GoogleCalAPI.create_event(Calendars.various.carrie, event)

    @classmethod
    def get_closest_event(cls, event: Event, history: List[LocationEventTemp]):
        matches = []
        for history_entry in history:
            try:
                address = Data.geo_location_dict[history_entry.name].address.__str__()
                time_zone = pytz.timezone(Data.geo_location_dict[history_entry.name].time_zone)
                history_entry.start = history_entry.start.astimezone(time_zone)
                history_entry.end = history_entry.end.astimezone(time_zone)
                category = Data.geo_location_dict[history_entry.name].category
                if event.location == address and category != 'Home':
                    event.start.date_time = event.start.date_time.astimezone(time_zone)
                    event.end.date_time = event.end.date_time.astimezone(time_zone)
                    offset = cls.calculate_time_offset(history_entry, event)
                    matches.append({'history_entry': history_entry, 'offset': offset})
            except KeyError:
                pass

        if matches:
            match = min(matches, key=lambda x: x.get('offset')).get('history_entry')
            event.start.date_time = match.start
            event.end.date_time = match.end
            GoogleCalAPI.update_event(event.calendar.get_cal_id(event.owner), event.event_id, event)
            return match

    @classmethod
    def print_events(cls, title: str, events: List[LocationEventTemp]):
        headers = ['START', 'END', 'LOCATION']
        width = [10, 10, 30]
        table_print = TablePrint(title, headers, width)

        for event in events:
            name = event.name if event.name != 'unknown' else ''
            start = event.start
            end = event.end
            if name:
                time_zone = Data.geo_location_dict[name].time_zone
                start = cls.ignore_dst(start, time_zone)
                end = cls.ignore_dst(end, time_zone)
                table_print.print_line([start.strftime('%H:%M:%S'), end.strftime('%H:%M:%S'), name])

    @classmethod
    def filter_geo_locations(cls, location: LocationEvent):
        geo_locations = {}
        for label, geo_location in Data.geo_location_dict.items():
            if geo_location.bounding_box:
                point_a = Point(location.latitude, location.longitude)
                if cls.get_distance(geo_location.bounding_box.intersection, point_a) < 2 * location.latitude:
                    geo_locations[label] = geo_location
        return geo_locations

    @staticmethod
    def is_work_day(events: List[LocationEventTemp]) -> bool:
        morning = any([event.name == 'Amplyfi' for event in events if event.start.time() < time(14)])
        afternoon = any([event.name == 'Amplyfi' for event in events if event.end.time() > time(12)])
        return morning and afternoon

    @staticmethod
    def create_default_event(history_entry: LocationEventTemp):
        time_zone = Data.geo_location_dict[history_entry.name].time_zone
        return Event(
            summary='New event',
            location=Data.geo_location_dict[history_entry.name].address.stringify(),
            description=history_entry.name,
            start=EventDateTime(date_time=history_entry.start, time_zone=time_zone),
            end=EventDateTime(date_time=history_entry.end, time_zone=time_zone)
        )

    @staticmethod
    def calculate_time_offset(event: LocationEventTemp, day_event: Event):
        start_diff = abs((event.start - day_event.start.date_time).total_seconds())
        end_diff = abs((event.end - day_event.end.date_time).total_seconds())
        return max(start_diff, end_diff)

    @staticmethod
    def get_distance(point1: Point, point2: Point):
        earth_radius = 6371e3
        phi_1 = radians(point1.latitude)
        phi_2 = radians(point2.latitude)
        df = radians(point2.latitude - point1.latitude)
        dl = radians(point2.longitude - point2.longitude)

        a = sin(df / 2) * sin(df / 2) + cos(phi_1) * cos(phi_2) * sin(dl / 2) * sin(dl / 2)
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return earth_radius * c

    @staticmethod
    def ignore_dst(event_time: datetime, time_zone: str):
        if pytz.timezone(time_zone).dst(event_time) != timedelta(0):
            return event_time + pytz.timezone(time_zone).dst(event_time)
        return event_time
