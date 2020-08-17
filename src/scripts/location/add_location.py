import pycountry
from pytz import country_timezones

from src.data.data import Data
from src.models.address import COUNTRY_ADDRESSES
from src.models.bounding_box import BoundingBox
from src.models.geo_location import GeoLocation
from src.models.point import Point
from src.scripts.location.location import LocationScript
from src.utils.input import Input
from src.utils.logger import Logger


class AddLocation(LocationScript):

    def __init__(self):
        super().__init__()

        self.bounding_box = None
        if Input.get_bool_input('Bounding box'):
            Logger.sub_sub_title('BOUNDING BOX')
            bounding_box = []
            for point in ['Bottom left', 'Top left', 'Top right', 'Bottom right']:
                lat_lon = Input.get_string_input(f'{point}', input_type='<lat>, <lon>')
                latitude, longitude = lat_lon.split(', ')
                bounding_box.append(Point(float(latitude), float(longitude)))
            self.bounding_box = BoundingBox(*bounding_box)

        Logger.sub_sub_title('DETAILS')
        self.label = Input.get_string_input('Label')
        self.category = Input.get_string_input('Category')
        self.address = Input.get_string_input('Address')

    def run(self):
        country = self.address.split(', ')[-1].replace('UK', 'United Kingdom')
        country_code = pycountry.countries.lookup(country).alpha_2

        if country_code in ['GB', 'BE']:
            address = COUNTRY_ADDRESSES[country_code.upper()].parse_from_string(self.address)
            time_zone = country_timezones(country_code)[0]
            time_zone = Input.get_string_input('Time zone', 'country/city', time_zone)

            Data.geo_location_dict.__add__(self.label,
                                           GeoLocation(self.category, address, time_zone, self.bounding_box))

            Logger.empty_line()
            Logger.bold('Added')
            return

        raise Exception('Invalid country')
