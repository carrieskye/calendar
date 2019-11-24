from geopy import Nominatim
from pytz import country_timezones

from src.models.address import UKAddress
from src.models.bounding_box import BoundingBox
from src.models.geo_location import GeoLocation
from src.models.point import Point
from src.utils.input import Input
from src.utils.output import Output
from src.utils.utils import Utils

GEO_LOCATIONS = Utils.read_json('data/geo_locations.json')

ADDRESSES = {
    'gb': UKAddress
}


def get_bounding_box():
    Output.make_title('BOUNDING BOX')

    bounding_box = []

    points = ['Bottom left', 'Top left', 'Top right', 'Bottom right']

    for point in points:
        lat_lon = Input.get_string_input(f'{point} latitude, longitude')
        latitude, longitude = lat_lon.split(', ')
        bounding_box.append(Point(float(latitude), float(longitude)))

    return BoundingBox(*bounding_box)


def add_geo_location():
    bounding_box = get_bounding_box()

    Output.make_title('DETAILS')

    label = Input.get_string_input('Label')
    category = Input.get_string_input('Category')
    address = Input.get_string_input('Address')
    geo_locator = Nominatim(user_agent='specify_your_app_name_here')
    location = geo_locator.reverse(f'{bounding_box.bottom_left.latitude}, {bounding_box.bottom_left.longitude}')
    country_code = location.raw.get('address').get('country_code')
    if country_code == 'gb':
        address = ADDRESSES[country_code].parse_from_string(address)
        time_zone = country_timezones(country_code)[0]
        time_zone = Input.get_string_input('Time zone', time_zone)

        geo_location = GeoLocation(label, category, address, time_zone, bounding_box)
        serialised_geo_location = geo_location.serialise()
        GEO_LOCATIONS.append(serialised_geo_location)
        Utils.write_json(GEO_LOCATIONS, 'data/geo_locations.json')

        Output.make_bold('\n\nAdded\n')


if __name__ == '__main__':
    add_geo_location()
