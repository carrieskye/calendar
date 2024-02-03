from __future__ import annotations

import operator
from collections import defaultdict
from datetime import datetime
from math import atan2, cos, radians, sin, sqrt
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field
from skye_comlib.utils.table_print import TablePrint

from src.models.point import Point


class LocationTimestamp(BaseModel):
    date_time: datetime
    latitude: float
    longitude: float
    accuracy: int
    location_id: Optional[str] = Field(None)

    @classmethod
    def from_database(cls, db_record: Tuple) -> LocationTimestamp:
        return cls(
            location_id=db_record[0],
            date_time=db_record[1],
            latitude=db_record[4],
            longitude=db_record[5],
            accuracy=db_record[9],
        )

    @classmethod
    def from_google(cls, takeout: dict) -> LocationTimestamp:
        latitude_e7 = takeout.get("latitudeE7")
        longitude_e7 = takeout.get("longitudeE7")
        return cls(
            date_time=datetime.fromtimestamp(int(takeout.get("timestampMs", 0)) / 1000),
            latitude=int(latitude_e7) / 10000000 if latitude_e7 else 0,
            longitude=int(longitude_e7) / 10000000 if longitude_e7 else 0,
            accuracy=int(takeout.get("accuracy", 0)),
        )

    @staticmethod
    def get_distance(lat_1: float, lon_1: float, lat_2: float, lon_2: float) -> float:
        earth_radius = 6371e3
        phi_1 = radians(lat_1)
        phi_2 = radians(lat_2)
        df = radians(lat_2 - lat_1)
        dl = radians(lon_2 - lon_1)

        a = sin(df / 2) * sin(df / 2) + cos(phi_1) * cos(phi_2) * sin(dl / 2) * sin(dl / 2)
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return earth_radius * c

    def get_point(self) -> Point:
        return Point(self.latitude, self.longitude)


class LocationTimestamps(List[LocationTimestamp]):
    def remove_duplicate_records(self) -> None:
        records_per_timestamp = defaultdict(list)
        for location in self:
            records_per_timestamp[location.date_time].append(location)
        duplicates = dict(filter(lambda x: len(x[1]) > 1, records_per_timestamp.items()))
        for locations in duplicates.values():
            for location in locations[1:]:
                self.remove(location)

    def filter_incorrect_locations(self) -> None:
        incorrect_locations = []
        for index, location in enumerate(self):
            group = self[max(0, index - 4) : min(len(self) - 1, index + 5)]
            if len([x for x in group if x.location_id == location.location_id]) == 1:
                incorrect_locations.append(index)
        for index in sorted(incorrect_locations, reverse=True):
            self.pop(index)

    def table_print(self, title: str) -> None:
        headers = ["TIME", "LAT - LON", "ACCURACY", "LOCATION"]
        table_print = TablePrint(title, headers, [8, 25, 10, 30])

        for location in self:
            table_print.print_line(
                [
                    location.date_time.strftime("%H:%M:%S"),
                    f"{location.latitude}, {location.longitude}",
                    location.accuracy,
                    location.location_id,
                ],
            )

    @classmethod
    def from_database(cls, db_records: List[Tuple]) -> LocationTimestamps:
        locations = cls()
        for db_record in db_records:
            locations.append(LocationTimestamp.from_database(db_record))
        locations.sort(key=operator.attrgetter("date_time"))
        locations.remove_duplicate_records()
        return locations
