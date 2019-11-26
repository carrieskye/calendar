from math import sqrt, radians, sin, cos, atan2, degrees

from geopy import Point as GeoPoint
from geopy.distance import geodesic

from src.models.address import Address, UKAddress
from src.models.bounding_box import BoundingBox
from src.models.location_event import LocationEvent
from src.models.point import Point


class GeoLocation:

    def __init__(self, label: str, category: str, address: Address, time_zone: str, bounding_box: BoundingBox):
        self.label = label
        self.category = category
        self.address = address
        self.time_zone = time_zone
        self.bounding_box = bounding_box

    def within_bounding_box(self, point: LocationEvent):
        bb = self.get_extended_bounding_box(point.accuracy)
        polygon = [bb.bottom_left, bb.top_left, bb.top_right, bb.bottom_right, bb.bottom_left]

        odd_nodes = False
        lat_point, lon_point = [point.latitude, point.longitude]

        j = 0
        for i in range(0, len(polygon)):
            j += 1
            if j == len(polygon):
                j = 0

            lat_1, lon_1 = [polygon[i].latitude, polygon[i].longitude]
            lat_2, lon_2 = [polygon[j].latitude, polygon[j].longitude]
            if ((lat_1 < lat_point) and (lat_2 >= lat_point)) or ((lat_2 < lat_point) and (lat_1 >= lat_point)):
                if lon_1 + (lat_point - lat_1) / (lat_2 - lat_1) * (lon_2 - lon_1) < lon_point:
                    odd_nodes = not odd_nodes
        return odd_nodes

    def get_extended_bounding_box(self, accuracy: int):
        bb = self.bounding_box
        d = accuracy / 1000

        new_bottom_left = GeoLocation.extend_point(bb.bottom_left, bb.top_left, bb.bottom_right, d)
        new_top_left = GeoLocation.extend_point(bb.top_left, bb.top_right, bb.bottom_left, d)
        new_top_right = GeoLocation.extend_point(bb.top_right, bb.bottom_right, bb.top_left, d)
        new_bottom_right = GeoLocation.extend_point(bb.bottom_right, bb.bottom_left, bb.top_right, d)

        return BoundingBox(new_bottom_left, new_top_left, new_top_right, new_bottom_right)

    def serialise(self):
        serialised = self.__dict__
        serialised['bounding_box'] = self.bounding_box.serialise()
        serialised['address'] = self.address.serialise()
        return serialised

    @staticmethod
    def deserialise(serialised: dict):
        serialised['bounding_box'] = BoundingBox.deserialise(serialised.get('bounding_box'))
        addresses = {
            'UK': UKAddress
        }
        serialised['address'] = addresses[serialised['address']['country_code']].deserialise(serialised.get('address'))
        return GeoLocation(**serialised)

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
    def get_bearing(point1: Point, point2: Point):
        lat_1 = radians(point1.latitude)
        lat_2 = radians(point2.latitude)
        delta_l = radians(abs(point1.longitude - point2.longitude))

        x = cos(lat_2) * sin(delta_l)
        y = (cos(lat_1) * sin(lat_2)) - (sin(lat_1) * cos(lat_2) * cos(delta_l))

        bearing = atan2(x, y)
        return degrees(bearing)

    @staticmethod
    def extend_point(target: Point, source_1: Point, source_2: Point, d):
        target = GeoPoint(target.latitude, target.longitude)
        source_1 = GeoPoint(source_1.latitude, source_1.longitude)
        source_2 = GeoPoint(source_2.latitude, source_2.longitude)

        if source_1.longitude < target.longitude:
            b_1 = GeoLocation.get_bearing(source_1, target)
        else:
            b_1 = GeoLocation.get_bearing(target, source_1) + 180

        if source_2.longitude < target.longitude:
            b_2 = GeoLocation.get_bearing(source_2, target)
        else:
            b_2 = GeoLocation.get_bearing(target, source_2) + 180

        if b_2 < b_1:
            b_2 += 360

        b = b_1 + ((b_2 - b_1) / 2)
        destination = geodesic(kilometers=sqrt(2 * pow(d, 2))).destination(target, b)
        return Point(destination.latitude, destination.longitude)
