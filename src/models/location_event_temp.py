from datetime import datetime
from typing import List


class LocationEventTemp:

    def __init__(self, name: str, events: List[str], start: datetime, end: datetime = None):
        self.name = name
        self.events = events
        self.start = start
        self.end = end

    def event_count(self):
        return len(self.events)
