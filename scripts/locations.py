import operator
from datetime import datetime, time

from dateutil.relativedelta import relativedelta
from geopy import Nominatim
from pytz import country_timezones

from scripts.script import Locations
from src.models.geo_location import GeoLocation
from src.models.location_event import LocationEvent
from src.models.location_event_temp import LocationEventTemp
from src.utils.input import Input
from src.utils.location import LocationUtils
from src.utils.output import Output
from src.utils.utils import Utils


class AddLocation(Locations):

    def __init__(self):
        super(AddLocation, self).__init__()

    def run(self):
        bounding_box = LocationUtils.get_bounding_box()

        Output.make_title('DETAILS')

        label = Input.get_string_input('Label')
        category = Input.get_string_input('Category')
        address = Input.get_string_input('Address')
        geo_locator = Nominatim(user_agent='specify_your_app_name_here')
        location = geo_locator.reverse(f'{bounding_box.bottom_left.latitude}, {bounding_box.bottom_left.longitude}')
        country_code = location.raw.get('address').get('country_code')
        if country_code == 'gb':
            address = self.utils.addresses[country_code].parse_from_string(address)
            time_zone = country_timezones(country_code)[0]
            time_zone = Input.get_string_input('Time zone', time_zone)

            geo_location = GeoLocation(label, category, address, time_zone, bounding_box)
            serialised_geo_location = geo_location.serialise()

            geo_locations = Utils.read_json('data/geo_locations.json')
            geo_locations.append(serialised_geo_location)
            Utils.write_json(geo_locations, 'data/geo_locations.json')

            Output.make_bold('\n\nAdded\n')


class Test(Locations):
    def __init__(self):
        super(Test, self).__init__()

        start = Input.get_date_input('Start', min_date=datetime(2019, 11, 20).date())
        self.start = datetime.combine(start, time(4, 0))
        self.end = self.start + relativedelta(days=1)
        self.larry = Input.get_bool_input('Larry')

    def run(self):
        Output.make_title('PROCESSING')

        results = LocationUtils.get_records(self.start, self.end)
        locations = [LocationEvent.from_database(result) for result in results]
        locations = sorted(locations, key=operator.attrgetter('date_time'))

        event_start = locations[0].date_time
        current_location = None
        events = []
        for location in locations:
            closest_location = self.utils.get_closest_location(location)

            if not current_location and closest_location:
                current_location = LocationEventTemp(closest_location, [closest_location], event_start)
            elif current_location:
                label = closest_location if closest_location else 'unknown'
                if current_location.name != label or location == locations[-1]:
                    current_location.end = location.date_time
                    events.append(current_location)
                    event_start = location.date_time
                    current_location = LocationEventTemp(label, [closest_location], event_start)
                else:
                    current_location.events.append(closest_location)

        group_events = LocationUtils.group_events(events)
        for group in group_events:
            print(group.start, group.end, group.name)
        self.utils.process_events(self.start.date(), group_events, self.larry)

        Output.make_bold('\nUpdated events\n')
