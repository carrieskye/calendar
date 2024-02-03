import json
from pathlib import Path
from typing import Dict

import jsonpickle
from skye_comlib.utils.file import File

from src.connectors.google_calendar import GoogleCalAPI
from src.models.calendar import Calendar


class CalendarDict(Dict[str, Calendar]):
    calendar_file = Path("data/calendars.json")

    def __init__(self) -> None:
        super().__init__()
        self.load_from_file()

    def load_from_file(self) -> None:
        for name, calendar in File.read_json(self.calendar_file).items():
            self[name] = Calendar.model_validate(calendar)

    def load_from_google(self) -> None:
        calendars = GoogleCalAPI.get_calendars()
        for calendar_name in calendars.keys():
            if not any(calendar_name.endswith(x) for x in ["larry"]):
                self[calendar_name] = Calendar.from_key(calendar_name, calendars)
        self.export_to_file()

    def export_to_file(self) -> None:
        File.write_json(
            contents={name: json.loads(jsonpickle.encode(calendar)) for name, calendar in self.items()},
            path=self.calendar_file,
        )
