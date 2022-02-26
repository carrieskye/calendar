import os
import re
from datetime import time, datetime

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from skye_comlib.utils.file import File
from skye_comlib.utils.input import Input
from skye_comlib.utils.logger import Logger

from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Calendars
from src.models.calendar import Owner
from src.models.event import Event
from src.models.event_datetime import EventDateTime
from src.scripts.activity.activity import ActivityScript


class ParseHayleyExportScript(ActivityScript):
    long_categories = {
        "cos": "Breastfeeding",
        "bf": "Breastfeeding",
        "blw": "Baby led weaning",
        "bt": "Bedtime routine",
        "cln": "Cleaning",
        "bm": "Breast milk",
        "exp": "Expressing",
        # 'for': 'Formula',
        "nap": "Nap",
        "np": "Nappy",
        "pl": "Play",
        "str": "Sleep training",
    }

    def __init__(self):
        super().__init__()

        start = Input.get_date_input("Start")
        self.start = datetime.combine(start, time(4, 0))
        days = Input.get_int_input("Days", "#days")
        self.end = self.start + relativedelta(days=days)
        self.owner = self.get_owner()
        self.location = self.get_location()

    def run(self):
        super().run()

        events = GoogleCalAPI.get_events(
            Calendars.chores, Owner.carrie, 1000, self.start, self.end
        )
        for event in events:
            GoogleCalAPI.delete_event(Calendars.chores.carrie, event.event_id)

        self.create_events()

    def create_events(self):
        for file in os.listdir("data/hayley"):
            if not file.endswith(".csv"):
                continue
            category = re.match(r"(?P<category>[a-z]*).csv", file).group("category")
            if category not in self.long_categories:
                continue
            export = File.read_csv(f"data/hayley/{file}")
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
                    start=EventDateTime(start, self.location.time_zone),
                    end=EventDateTime(end, self.location.time_zone),
                )
                Logger.log(event.summary)
                GoogleCalAPI.create_event(Calendars.chores.carrie, event)
