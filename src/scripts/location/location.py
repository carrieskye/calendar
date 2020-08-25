from abc import ABC
from datetime import datetime
from math import radians, sin, atan2, sqrt, cos

from src.connectors.own_tracks import OwnTracks
from src.data.data import Data
from src.models.calendar import Owner
from src.models.location_timestamp import LocationTimestamp, LocationTimestamps
from src.models.point import Point
from src.scripts.script import Script


class LocationScript(Script, ABC):

    @classmethod
    def get_location_timestamps(cls, start: datetime, end: datetime, owner: Owner) -> LocationTimestamps:
        results = OwnTracks.get_records(start, end, owner)
        locations = LocationTimestamps.from_database(results)

        for location in locations:
            location.location_id = cls.get_closest_location(location)

        return locations

    @classmethod
    def get_closest_location(cls, location_timestamp: LocationTimestamp) -> str:
        matches = []
        geo_locations = cls.filter_geo_locations(location_timestamp)
        for label, geo_location in geo_locations.items():
            if geo_location.within_bounding_box(location_timestamp):
                matches.append(label)
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            distances = {}
            for match in matches:
                intersection = Data.geo_location_dict[match].bounding_box.intersection
                distances[match] = cls.get_distance(location_timestamp.get_point(), intersection)
            match = min(distances.items(), key=lambda x: x[1])
            return match[0]

    @classmethod
    def filter_geo_locations(cls, location_timestamp: LocationTimestamp):
        geo_locations = {}
        for label, geo_location in Data.geo_location_dict.items():
            if geo_location.bounding_box:
                point_a = Point(location_timestamp.latitude, location_timestamp.longitude)
                if cls.get_distance(geo_location.bounding_box.intersection, point_a) < 2 * location_timestamp.latitude:
                    geo_locations[label] = geo_location
        return geo_locations

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
