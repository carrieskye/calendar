import operator
import sys
from datetime import datetime
from typing import List

import pytz
from dateutil.relativedelta import relativedelta

from data.location_history_data import LocationHistoryData
from src.connectors.google_calendar import GoogleCalendarAPI
from src.models.event import Event
from src.models.event_datetime import EventDateTime
from src.models.frequent_location import FrequentLocation
from src.models.location_event import LocationEvent
from src.utils.utils import Utils

GOOGLE_CALENDAR = GoogleCalendarAPI()

MIN_EVENT_TIME = 30
MAX_DISTANCE = 20

ADDRESSES = LocationHistoryData.get_addresses()
FREQUENT_LOCATIONS = LocationHistoryData.get_frequent_locations()
BAD_LOCATIONS = LocationHistoryData.get_bad_locations()


def get_closest_location(lat, lon, accuracy, previous_name):
    distances = {}
    for title, frequent_location in FREQUENT_LOCATIONS.items():
        assert isinstance(frequent_location, FrequentLocation)
        location_lat = frequent_location.latitude
        location_lon = frequent_location.longitude
        distances[title] = LocationEvent.get_distance(lat, lon, location_lat, location_lon)

    closest_location, distance = min(distances.items(), key=lambda x: x[1])

    if previous_name in distances:
        if FREQUENT_LOCATIONS[previous_name].address == 'campus_proximus' and 'auditorium' not in previous_name:
            close_to_previous = distances[previous_name] < 15
        else:
            close_to_previous = distances[previous_name] < accuracy
        if close_to_previous:
            return previous_name, distances[previous_name]

    radius = FREQUENT_LOCATIONS[closest_location].radius + accuracy
    closest_location = closest_location if distance < radius else 'unknown'
    return closest_location, distance


def get_day_events(year: int, month: int, day: int):
    start = datetime(year, month, day)
    end = start + relativedelta(days=1)

    return [Event.get_event(event, calendar_id) for calendar_id in GOOGLE_CALENDAR.calendars.values()
            for event in GOOGLE_CALENDAR.get_events(calendar_id, 100, start, end)]


def get_closest_event(event: Event, history: List[dict]):
    matches = []
    for history_entry in history:
        try:
            address_key = FREQUENT_LOCATIONS[history_entry.get('location')].address
            address = ADDRESSES[address_key]
            time_zone = pytz.timezone(address.time_zone)
            history_entry['start'] = history_entry.get('start').astimezone(time_zone)
            history_entry['end'] = history_entry.get('end').astimezone(time_zone)
            category = FREQUENT_LOCATIONS[history_entry.get('location')].category
            if event.location == address.address and category != 'home':
                event.start.date_time = event.start.date_time.astimezone(time_zone)
                event.end.date_time = event.end.date_time.astimezone(time_zone)
                offset = calculate_time_offset(history_entry, event)
                matches.append({'history_entry': history_entry, 'offset': offset})
        except KeyError:
            pass

    if matches:
        match = min(matches, key=lambda x: x.get('offset')).get('history_entry')
        event.start.date_time = match.get('start')
        event.end.date_time = match.get('end')
        GOOGLE_CALENDAR.update_event(event.calendar_id, event.event_id, event)
        return match


def calculate_time_offset(event: dict, day_event: Event):
    start_diff = abs((event.get('start') - day_event.start.date_time).total_seconds())
    end_diff = abs((event.get('end') - day_event.end.date_time).total_seconds())
    return max(start_diff, end_diff)


def create_default_event(history_entry: dict):
    address = ADDRESSES[FREQUENT_LOCATIONS[history_entry.get('location')].address]
    return Event(
        summary='New event',
        location=address.address,
        description=history_entry.get('location'),
        start=EventDateTime(date_time=history_entry.get('start'), time_zone=address.time_zone),
        end=EventDateTime(date_time=history_entry.get('end'), time_zone=address.time_zone)
    )


def process_events(year: int, month: int, day: int, history: List[dict], larry: bool):
    events = get_day_events(year, month, day)
    for event in events:
        popped_event = get_closest_event(event, history)
        if popped_event and (event.calendar != 'work' or not larry):
            history.pop(history.index(popped_event))

    for remaining_entry in history:
        unknown = remaining_entry.get('location') == 'unknown'
        too_short = remaining_entry.get('start') + relativedelta(minutes=30) >= remaining_entry.get('end')
        category = FREQUENT_LOCATIONS[remaining_entry.get('location')].category if not unknown else 'unknown'
        home = category == 'home'
        if not (too_short or home):
            if not unknown:
                event = create_default_event(remaining_entry)
                calendar_id = GOOGLE_CALENDAR.get_calendar_id('various')
                GOOGLE_CALENDAR.create_event(calendar_id, event)
            else:
                print(remaining_entry)


def close_to_bad_locations(latitude, longitude):
    for bad_location in BAD_LOCATIONS:
        if LocationEvent.get_distance(latitude, longitude, bad_location.get('latitude'),
                                      bad_location.get('longitude')) < 20:
            return True
    return False


def run(year: str, month: str, day: str, larry: str = 'false'):
    year, month, day = (int(year), int(month), int(day))
    results = Utils.read_json(f'data/location_history/{year}/{month:02d}/{day:02d}.json')
    locations = [LocationEvent.from_google(result) for result in results]
    locations = sorted(locations, key=operator.attrgetter('date_time'))

    event_start = locations[0].date_time
    event_end = locations[0].date_time
    current_location, new_location, last_amplyfi_end = (None, None, None)
    error_count = 0
    history = []
    for location in locations:
        if not close_to_bad_locations(location.latitude, location.longitude):
            name, distance = get_closest_location(location.latitude, location.longitude, location.accuracy,
                                                  current_location)
            print(location.date_time.isoformat()[:16], name, distance, location.accuracy,
                  f'{location.latitude},{location.longitude}')

            if not current_location:
                current_location = name
            else:
                if location == locations[-1]:
                    event_end = location.date_time
                    history.append({'start': event_start, 'end': event_end, 'location': current_location})
                    current_location = new_location
                    event_start = event_end
                elif name != current_location:
                    error_count += 1
                    if error_count > 1:
                        same_location = new_location == name
                        if error_count > 2:
                            if new_location == name and same_location:
                                short_event = abs((event_end - event_start).total_seconds()) < 1800
                                bad_location = current_location == 'unknown'
                                if history and (short_event or bad_location) and new_location == history[-1].get(
                                        'location'):
                                    latest_history_entry = history.pop(-1)
                                    event_start = latest_history_entry.get('start')
                                    current_location = new_location
                                elif history and current_location == 'unknown' and new_location == 'tramshed_tech':
                                    current_location = new_location
                                else:
                                    history.append(
                                        {'start': event_start, 'end': event_end, 'location': current_location})
                                    current_location = new_location
                                    event_start = event_end
                                error_count = 0
                    else:
                        event_end = location.date_time
                    new_location = name

                else:
                    error_count = 0

    print()
    for entry in history:
        time_zone = pytz.timezone('Europe/London')
        print(entry.get('start').astimezone(time_zone), entry.get('end').astimezone(time_zone),
              entry.get('location'))
    print()
    # process_events(year, month, day, history, strtobool(larry))


if __name__ == '__main__':
    # LocationHistoryData.get_labeled_places()
    if len(sys.argv) > 2:
        globals()[sys.argv[1]](*sys.argv[2:])
    else:
        globals()[sys.argv[1]]()
