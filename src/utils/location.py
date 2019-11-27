from datetime import datetime, time, date
from math import radians, sin, atan2, sqrt, cos
from typing import List

import psycopg2
import pytz
from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalendarAPI
from src.models.address import UKAddress, BEAddress
from src.models.bounding_box import BoundingBox
from src.models.event import Event
from src.models.event_datetime import EventDateTime
from src.models.geo_location import GeoLocation
from src.models.location_event import LocationEvent
from src.models.location_event_temp import LocationEventTemp
from src.models.point import Point
from src.utils.input import Input
from src.utils.output import Output
from src.utils.utils import Utils


class LocationUtils:

    def __init__(self):
        self.google_cal = GoogleCalendarAPI()
        self.geo_locations = {geo_location.get('label'): GeoLocation.deserialise(geo_location)
                              for geo_location in Utils.read_json('data/geo_locations.json')}
        self.addresses = {
            'gb': UKAddress,
            'be': BEAddress
        }

    @staticmethod
    def get_bounding_box():
        Output.make_title('BOUNDING BOX')

        bounding_box = []

        points = ['Bottom left', 'Top left', 'Top right', 'Bottom right']

        for point in points:
            lat_lon = Input.get_string_input(f'{point} latitude, longitude')
            latitude, longitude = lat_lon.split(', ')
            bounding_box.append(Point(float(latitude), float(longitude)))

        bounding_box.append(LocationUtils.get_intersection(*bounding_box))
        return BoundingBox(*bounding_box)

    @staticmethod
    def get_intersection(bottom_left: Point, top_left: Point, top_right: Point, bottom_right: Point):
        # m = (y_2 - y_1) / (x_2 - x_1)
        # y = mx + b
        # b = -mx + y
        m_1 = (top_right.longitude - bottom_left.longitude) / (top_right.latitude - bottom_left.latitude)
        b_1 = - (top_right.latitude * m_1) + top_right.longitude
        m_2 = (bottom_right.longitude - top_left.longitude) / (bottom_right.latitude - top_left.latitude)
        b_2 = - (bottom_right.latitude * m_2) + bottom_right.longitude

        # m_1 * x + b_1 = m_2 * x + b_2
        # m_1 * x - m_2 * x = b_2 - b_1
        # (m_1 - m_2) * x = b_2 - b_1
        x = (b_2 - b_1) / (m_1 - m_2)
        y = x * m_1 + b_1
        return Point(x, y)

    @staticmethod
    def get_records(start: datetime, end: datetime, user_id: int = 3, accuracy: int = 20):
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

    @staticmethod
    def group_events(events: List[LocationEventTemp]):
        grouped_events = []
        index = 0

        while index < len(events):
            event = events[index]

            if (event.name == 'unknown' or len(event.events) < 3) and grouped_events:
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

        return LocationUtils.clean_work(grouped_events)

    @staticmethod
    def clean_work(events: List[LocationEventTemp]):
        cleaned_events = []
        index = 0

        work_day = LocationUtils.is_work_day(events)
        while index < len(events):
            event = events[index]

            morning = event.start.time() < time(12)
            noon = event.start.time() > time(12) and time(4) < event.end.time() < time(14)
            afternoon = event.end.time() > time(14)

            if event.name == 'Tramshed Tech' and (morning or afternoon):
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
            elif work_day and event.name != 'Amplyfi' and noon and events[index + 1].name == 'Amplyfi':
                first_index = len(cleaned_events)
                while first_index > 2 and cleaned_events[first_index - 1].name != 'Amplyfi':
                    first_index -= 1
                start = cleaned_events[first_index].start
                event_list = []
                for x in range(len(cleaned_events) - 1, first_index - 1, -1):
                    event_list += cleaned_events.pop(x).events
                event_list += event.events
                cleaned_events.append(LocationEventTemp('Tramshed Tech', event_list, start, event.end))

            else:
                cleaned_events.append(event)
            index += 1

        return cleaned_events

    @staticmethod
    def is_work_day(events: List[LocationEventTemp]):
        morning = any([event.name == 'Amplyfi' for event in events if event.start.time() < time(14)])
        afternoon = any([event.name == 'Amplyfi' for event in events if event.end.time() > time(12)])
        return morning and afternoon

    def get_closest_location(self, location: LocationEvent):
        matches = []
        for label, geo_location in self.geo_locations.items():
            if geo_location.within_bounding_box(location):
                matches.append(label)
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            distances = {}
            for match in matches:
                intersection = self.geo_locations[match].bounding_box.intersection
                distances[match] = LocationUtils.get_distance(location.get_point(), intersection)
            match = min(distances.items(), key=lambda x: x[1])
            return match[0]

    def process_events(self, start: date, history: List[LocationEventTemp], larry: bool):
        events = self.get_day_events(start)
        for event in events:
            popped_event = self.get_closest_event(event, history)
            if popped_event and (event.calendar != 'work' or not larry):
                history.pop(history.index(popped_event))

        for remaining_entry in history:
            unknown = remaining_entry.name == 'unknown'
            too_short = remaining_entry.start + relativedelta(minutes=30) >= remaining_entry.end
            category = self.geo_locations[remaining_entry.name].category if not unknown else 'unknown'
            home = category == 'Home'
            if not (too_short or home):
                if not unknown:
                    event = self.create_default_event(remaining_entry)
                    calendar_id = self.google_cal.get_calendar_id('various')
                    self.google_cal.create_event(calendar_id, event)
                else:
                    print(remaining_entry)

    def create_default_event(self, history_entry: LocationEventTemp):
        time_zone = self.geo_locations[history_entry.name].time_zone
        return Event(
            summary='New event',
            location=self.geo_locations[history_entry.name].address.stringify(),
            description=history_entry.name,
            start=EventDateTime(date_time=history_entry.start, time_zone=time_zone),
            end=EventDateTime(date_time=history_entry.end, time_zone=time_zone)
        )

    def get_day_events(self, start: date):
        start = datetime.combine(start, time(4, 0))
        end = start + relativedelta(days=1)

        return [Event.get_event(event, calendar_id) for calendar_id in self.google_cal.calendars.values()
                for event in self.google_cal.get_events(calendar_id, 100, start, end)]

    def get_closest_event(self, event: Event, history: List[LocationEventTemp]):
        matches = []
        for history_entry in history:
            try:
                address = self.geo_locations[history_entry.name].address.stringify()
                time_zone = pytz.timezone(self.geo_locations[history_entry.name].time_zone)
                history_entry.start = history_entry.start.astimezone(time_zone)
                history_entry.end = history_entry.end.astimezone(time_zone)
                category = self.geo_locations[history_entry.name].category
                if event.location == address and category != 'Home':
                    event.start.date_time = event.start.date_time.astimezone(time_zone)
                    event.end.date_time = event.end.date_time.astimezone(time_zone)
                    offset = self.calculate_time_offset(history_entry, event)
                    matches.append({'history_entry': history_entry, 'offset': offset})
            except KeyError:
                pass

        if matches:
            match = min(matches, key=lambda x: x.get('offset')).get('history_entry')
            print(match.start, match.end)
            event.start.date_time = match.start
            event.end.date_time = match.end
            self.google_cal.update_event(event.calendar_id, event.event_id, event)
            return match

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
