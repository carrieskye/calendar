import logging
import os
import re
from datetime import datetime, time
from pathlib import Path

from dateutil.parser import parse  # type: ignore
from dateutil.relativedelta import relativedelta  # type: ignore
from skye_comlib.utils.file import File
from skye_comlib.utils.input import Input

from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Calendars
from src.models.calendar import Owner
from src.models.event import Event
from src.models.event_datetime import EventDateTime
from src.scripts.activity.activity_script import ActivityScript


class ParseHayleyExportScript(ActivityScript):
    long_categories = {
        "bfs": "Breastfeeding",
        "bf": "Breastfeeding",
        "blw": "Baby led weaning",
        "bt": "Bedtime routine",
        "cln": "Cleaning",
        "bm": "Breast milk",
        "exp": "Expressing",
        "for": "Formula",
        "nap": "Nap",
        "np": "Nappy",
        "pt": "Potty",
        "pl": "Play",
        "str": "Sleep training",
    }

    def __init__(self) -> None:
        super().__init__()

        start = Input.get_date_input("Start")
        self.start = datetime.combine(start, time(4))
        days = Input.get_int_input("Days", "#days")
        self.end = self.start + relativedelta(days=days)
        self.owner = self.get_owner()
        self.location = self.get_location()

    def run(self) -> None:
        super().run()

        events = GoogleCalAPI.get_events(Calendars.chores, Owner.carrie, 1000, self.start, self.end)
        for event in events:
            GoogleCalAPI.delete_event(Calendars.chores.carrie, event.event_id)

        self.create_events()

    def create_events(self) -> None:
        base_dir = Path("data/hayley")
        for file in os.listdir(base_dir):
            if not file.endswith(".csv"):
                continue
            match = re.match(r"(?P<category>[a-z]*).csv", file)
            if not match:
                continue
            category = match.group("category")
            if category not in self.long_categories:
                continue
            export = File.read_csv(base_dir / file)
            for item in export:
                if not item["weekday"] or item["weekday"] == "#N/A":
                    continue
                start = parse(item["actual"] + " " + item["start"])
                if not self.start < start < self.end:
                    continue
                hours, minutes = item["total"].split(":")
                end = start + relativedelta(hours=int(hours), minutes=int(minutes))

                if category == "cln":
                    summary = item["type"].capitalize()
                elif category == "blw":
                    summary = item["meal"].capitalize()
                else:
                    summary = self.long_categories[category]

                event = Event(
                    summary=summary,
                    location=self.location.address.__str__(),
                    start=EventDateTime(date_time=start, time_zone=self.location.time_zone),
                    end=EventDateTime(date_time=end, time_zone=self.location.time_zone),
                )
                logging.info(event.summary)
                GoogleCalAPI.create_event(Calendars.chores.carrie, event)
