from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

import pytz
from dateutil.relativedelta import relativedelta
from skye_comlib.utils.table_print import TablePrint

from src.data.data import Data
from src.models.location_timestamp import LocationTimestamps, LocationTimestamp


class LocationEvent:
    def __init__(
        self,
        start: datetime,
        end: datetime,
        timestamps: List[LocationTimestamp],
        location_id: str,
    ):
        self.start = start
        self.end = end
        self.timestamps = timestamps
        self.location_id = location_id

    @classmethod
    def from_location_timestamp(cls, timestamp: LocationTimestamp) -> LocationEvent:
        return cls(
            timestamp.date_time, timestamp.date_time, [timestamp], timestamp.location_id
        )


class LocationEvents(List[LocationEvent]):
    def table_print(self, title: str):
        headers = ["START", "END", "DURATION", "RECORDS", "LOCATION"]
        width = [9, 9, 9, 7, 30]
        table_print = TablePrint(title, headers, width)
        first_location = [x.location_id for x in self if x.location_id][0]
        time_zone = Data.geo_location_dict[first_location].time_zone

        for event in self:
            if event.location_id:
                time_zone = Data.geo_location_dict[event.location_id].time_zone
            start = self.ignore_dst(event.start, time_zone)
            end = self.ignore_dst(event.end, time_zone)
            table_print.print_line(
                [
                    start.strftime("%H:%M:%S"),
                    end.strftime("%H:%M:%S"),
                    end - start if end - start else "0:00:00",
                    len(event.timestamps),
                    event.location_id,
                ]
            )

    def merge_events(self):
        to_merge = []
        for index, event in enumerate(self):
            if index in [0, len(self) - 1] or event.location_id:
                continue
            if self[index - 1].location_id != self[index + 1].location_id:
                continue
            if event.start + relativedelta(minutes=5) <= event.end:
                continue
            if len(event.timestamps) >= 10:
                continue
            if event.start + relativedelta(minutes=2) <= event.end:
                if len(event.timestamps) >= 5:
                    continue
            to_merge.append(index)

        for index in sorted(to_merge, reverse=True):
            self[index - 1].timestamps += self[index + 1].timestamps
            self[index - 1].end = self[index + 1].end
            self.pop(index)
            self.pop(index)

        self.table_print("Merged events")

    def remove_short_events(self):
        to_remove = []
        for index, event in enumerate(self):
            if not event.location_id:
                continue
            if (
                len(event.timestamps) < 5
                and event.start + relativedelta(minutes=5) > event.end
            ):
                to_remove.append(index)
            elif event.start + relativedelta(minutes=2) > event.end:
                to_remove.append(index)

        for index in sorted(to_remove, reverse=True):
            for timestamp in self[index].timestamps:
                timestamp.location_id = ""

            self[index - 1].timestamps += (
                self[index].timestamps + self[index + 1].timestamps
            )
            self[index - 1].end = self[index].end
            self.pop(index)

        to_remove = []
        for index, event in enumerate(self[:-1]):
            if event.location_id == self[index + 1].location_id:
                group_index = index
                while (
                    group_index < len(self) - 1
                    and event.location_id == self[group_index + 1].location_id
                ):
                    group_index += 1
                    self[index].timestamps += self[group_index].timestamps
                    to_remove.append(group_index)
                event.end = self[group_index].end

        for index in sorted(to_remove, reverse=True):
            self.pop(index)

        self.table_print("Without short events")

    @classmethod
    def from_location_timestamps(cls, timestamps: LocationTimestamps) -> LocationEvents:
        location_events = cls()
        current_event = LocationEvent.from_location_timestamp(timestamps[0])
        for timestamp in timestamps[1:]:
            if timestamp.location_id == current_event.location_id:
                current_event.end = timestamp.date_time
                current_event.timestamps.append(timestamp)
            else:
                new_event = LocationEvent.from_location_timestamp(timestamp)
                if not new_event.location_id:
                    new_event.start = current_event.end
                if not current_event.location_id:
                    current_event.end = new_event.start
                location_events.append(current_event)
                current_event = new_event

        location_events.append(current_event)
        location_events.table_print("Location events")
        return location_events

    @staticmethod
    def ignore_dst(event_time: datetime, time_zone: str):
        if pytz.timezone(time_zone).dst(event_time) != timedelta(0):
            return event_time + pytz.timezone(time_zone).dst(event_time)
        return event_time
