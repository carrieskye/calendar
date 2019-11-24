import operator
from datetime import datetime

import psycopg2
from dateutil.relativedelta import relativedelta

from src.models.geo_location import GeoLocation
from src.models.location_event import LocationEvent
from src.utils.utils import Utils

GEO_LOCATIONS = [GeoLocation.deserialise(geo_location) for geo_location in Utils.read_json('data/geo_locations.json')]


def get_records(start: datetime, end: datetime):
    conditions = f'WHERE time > \'{start.isoformat()}\' AND time < \'{end.isoformat()}\' AND user_id = 3 AND accuracy < 20'
    query = f'SELECT * FROM public.positions {conditions}'

    conn = psycopg2.connect(host='nuc', database='ulogger', user='postgres', password='catsies')
    cur = conn.cursor()
    cur.execute(query)
    records = cur.fetchall()
    conn.close()
    return records


if __name__ == '__main__':

    start = datetime(2019, 11, 20, 4, 0)
    end = start + relativedelta(days=1)
    results = get_records(start, end)
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
