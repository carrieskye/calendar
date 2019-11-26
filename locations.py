import operator
from datetime import datetime

from dateutil.relativedelta import relativedelta

from src.models.geo_location import GeoLocation
from src.models.location_event import LocationEvent
from src.utils.location import LocationUtils
from src.utils.utils import Utils

GEO_LOCATIONS = [GeoLocation.deserialise(geo_location) for geo_location in Utils.read_json('data/geo_locations.json')]

if __name__ == '__main__':

    start = datetime(2019, 11, 20, 4, 0)
    end = start + relativedelta(days=1)
    results = LocationUtils.get_records(start, end)
    locations = [LocationEvent.from_database(result) for result in results]
    locations = sorted(locations, key=operator.attrgetter('date_time'))

    for location in locations:
        match = False
        for geo_location in GEO_LOCATIONS:
            if geo_location.within_bounding_box(location):
                match = True
                print(geo_location.label)
        if not match:
            print('unknown', location.latitude, location.longitude, location.accuracy)
