from src.models.event_datetime import EventDateTime
from src.utils.utils import Utils

SUMMARIES = Utils.read_json('data/summaries.json')
LOCATIONS = Utils.read_json('data/locations.json')
CLASSROOMS = Utils.read_json('data/classrooms.json')
SHORT_LOCATIONS = Utils.read_json('data/short_locations.json')


class Event:

    def __init__(self, summary: str, location: str, start: EventDateTime, end: EventDateTime, description: str = '',
                 event_id: str = '', calendar: str = '', calendar_id: str = ''):
        self.summary = summary
        self.location = location if location else ''
        self.description = description if description else ''
        self.start = start
        self.end = end
        self.event_id = event_id
        self.calendar = calendar
        self.calendar_id = calendar_id

    def to_dict(self):
        return {
            'summary': self.summary,
            'location': self.location,
            'description': self.description,
            'start': self.start.to_dict(),
            'end': self.end.to_dict(),
            'visibility': 'default'
        }

    def update_summary(self):
        if not self.summary:
            self.summary = ''

        if self.summary.lower() in SUMMARIES:
            self.summary = SUMMARIES[self.summary.lower()]

    def update_location_and_description(self):
        if not self.location:
            self.location = ''
        if not self.description:
            self.description = ''

        old_location = self.location
        # old_location = self.location.replace(' - ', ' ')
        # old_location = old_location.split(' (')[0]

        if old_location in Event.get_locations() or not old_location:
            self.location = old_location
            return

        if old_location.lower() in Event.get_classrooms():
            classroom = Event.get_classrooms()[old_location.lower()]
            self.location = Event.get_old_locations()[classroom.get('campus')]
            self.description = classroom.get('classroom')

        if old_location.lower() in Event.get_old_locations():
            self.location = Event.get_old_locations()[old_location.lower()]

    def update_start_and_end(self):
        # Use the location to update the time zones
        if self.location:
            time_zone = self.get_time_zones_by_location(self.location, self.start, self.end)
            self.start.time_zone = time_zone
            self.end.time_zone = time_zone

        # If we don't have a location, check if it's a transport event and use the description to get the time zones
        elif ' > ' in self.description:
            self.update_transport_time_zones()

        else:
            raise Exception(f'NO LOCATION: {self.to_dict()}')

    @staticmethod
    def get_time_zones_by_location(location: str, start: EventDateTime, end: EventDateTime):
        # If we have the location, get the time zone for the location
        if location in Event.get_locations():
            return Event.get_locations()[location]

        # If we have the time zone, add the location and its time zone
        elif start.time_zone:
            if start.time_zone == end.time_zone:
                try:
                    Event.add_location(location, start.time_zone)
                except Exception as e:
                    raise Exception(f'FAILED TO ADD LOCATION ON {start.date_time}: {e}')
                return start.time_zone

        # If we don't have the time zone, get the country by the location and use that to get the time zone
        else:
            time_zone = Event.get_time_zone_by_country(location.split(', ')[-1])
            if time_zone:
                return time_zone

        raise Exception(F'NEW LOCATION: {location} on {start.date_time}')

    def update_transport_time_zones(self):
        departure, destination = self.description.split(' (')[0].split(' > ')
        self.start.time_zone = self.add_transport_time_zone(departure, self.start.time_zone)
        self.end.time_zone = self.add_transport_time_zone(destination, self.end.time_zone)

    @staticmethod
    def add_transport_time_zone(location, time_zone):
        try:
            return Event.get_short_locations()[location]
        except KeyError:
            if time_zone:
                SHORT_LOCATIONS[time_zone].append(location)
                Utils.write_json(SHORT_LOCATIONS, 'data/short_locations.json')
                return time_zone
            else:
                raise Exception(f'FAILED TO ADD TIME ZONE FOR {location}.')

    @staticmethod
    def add_location(location, time_zone):
        if time_zone not in LOCATIONS:
            LOCATIONS[time_zone] = {'countries': [location.split(', ')[-1]], 'locations': {}}
        else:
            countries = LOCATIONS[time_zone]['countries']
            if location.split(', ')[-1] not in countries:
                time_zone = Event.get_time_zone_by_country(location.split(', ')[-1])
                if not time_zone:
                    raise Exception(f'ILLEGAL VALUE: {location} for {time_zone}')
        LOCATIONS[time_zone]['locations'][location.lower()] = location
        Utils.write_json(LOCATIONS, 'data/locations.json')

    @staticmethod
    def get_old_locations():
        return {location_old: location_new
                for time_zone, value in LOCATIONS.items()
                for location_old, location_new in value['locations'].items()}

    @staticmethod
    def get_locations():
        return {location_new: time_zone
                for time_zone, value in LOCATIONS.items()
                for location_old, location_new in value['locations'].items()}

    @staticmethod
    def get_short_locations():
        return {location: time_zone
                for time_zone, locations in SHORT_LOCATIONS.items()
                for location in locations}

    @staticmethod
    def get_classrooms():
        return {location: {'campus': campus, 'classroom': classroom}
                for campus, campus_classrooms in Utils.read_json('data/classrooms.json').items()
                for location, classroom in campus_classrooms.items()}

    @staticmethod
    def get_time_zone_by_country(country):
        return {country: time_zone for time_zone, value in LOCATIONS.items()
                for country in value['countries']}.get(country)

    @staticmethod
    def get_event(original: dict, calendar_id: str, calendar: str = ''):
        return Event(
            summary=original.get('summary'),
            location=original.get('location'),
            description=original.get('description'),
            start=EventDateTime.get_event_date_time(original.get('start')),
            end=EventDateTime.get_event_date_time(original.get('end')),
            event_id=original.get('id'),
            calendar=calendar if calendar else Event.get_calendar_name(calendar_id),
            calendar_id=calendar_id
        )

    @staticmethod
    def equals(event_1: dict, event_2: dict):
        keys = ['summary', 'location', 'description', 'start', 'end', 'event_id']
        return any(event_1.get(key) != event_2.get(key) for key in keys)

    @staticmethod
    def get_calendar_name(calendar_id: str):
        calendars = Utils.read_json('exports/calendars.json')
        hits = [cal_name for cal_name, cal_id in calendars.items() if cal_id == calendar_id]
        return hits[0] if hits else ''
