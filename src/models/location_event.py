from __future__ import annotations

from datetime import datetime
from math import radians, atan2, sin, cos, sqrt
from typing import Tuple

from src.models.point import Point


class LocationEvent:

    def __init__(self, date_time, latitude, longitude, accuracy, location_id=''):
        self.date_time = date_time
        self.latitude = latitude
        self.longitude = longitude
        self.accuracy = accuracy
        self.location_id = location_id

    @classmethod
    def from_database(cls, db_record: Tuple) -> LocationEvent:
        return cls(
            location_id=db_record[0],
            date_time=db_record[1],
            latitude=db_record[4],
            longitude=db_record[5],
            accuracy=db_record[9]
        )

    @classmethod
    def from_google(cls, takeout: dict) -> LocationEvent:
        return cls(
            date_time=datetime.fromtimestamp(int(takeout.get('timestampMs')) / 1000),
            latitude=int(takeout.get('latitudeE7')) / 10000000,
            longitude=int(takeout.get('longitudeE7')) / 10000000,
            accuracy=int(takeout.get('accuracy'))
        )

    @staticmethod
    def get_distance(lat_1, lon_1, lat_2, lon_2):
        earth_radius = 6371e3
        phi_1 = radians(lat_1)
        phi_2 = radians(lat_2)
        df = radians(lat_2 - lat_1)
        dl = radians(lon_2 - lon_1)

        a = sin(df / 2) * sin(df / 2) + cos(phi_1) * cos(phi_2) * sin(dl / 2) * sin(dl / 2)
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return earth_radius * c

    def get_point(self):
        return Point(self.latitude, self.longitude)
