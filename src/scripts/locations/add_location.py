from pytz import country_timezones

from src.data.data import Data
from src.models.address import COUNTRY_ADDRESSES
from src.models.bounding_box import BoundingBox
from src.models.geo_location import GeoLocation
from src.models.point import Point
from src.scripts.script import Locations
from src.utils.input import Input
from src.utils.output import Output


class AddLocation(Locations):

    def __init__(self):
        super().__init__()

        Output.make_title('BOUNDING BOX')
        bounding_box = []
        for point in ['Bottom left', 'Top left', 'Top right', 'Bottom right']:
            lat_lon = Input.get_string_input(f'{point} latitude, longitude')
            latitude, longitude = lat_lon.split(', ')
            bounding_box.append(Point(float(latitude), float(longitude)))

        self.bounding_box = BoundingBox(*bounding_box)

        Output.make_title('DETAILS')
        self.label = Input.get_string_input('Label')
        self.category = Input.get_string_input('Category')
        self.address = Input.get_string_input('Address')

    def run(self):
        location = self.bounding_box.get_address()
        country_code = location.raw.get('address').get('country_code')

        if country_code in ['gb', 'be']:
            address = COUNTRY_ADDRESSES[country_code.upper()].parse_from_string(self.address)
            time_zone = country_timezones(country_code)[0]
            time_zone = Input.get_string_input('Time zone', 'country/city', time_zone)

            Data.geo_locations.__add__(self.label, GeoLocation(self.category, address, time_zone, self.bounding_box))

            Output.make_bold('\n\nAdded\n')
            return

        raise Exception('Invalid country')
