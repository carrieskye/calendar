import json
from typing import Dict

import jsonpickle

from src.connectors.google_calendar import GoogleCalAPI
from src.models.calendar import Calendar
from src.utils.file import File
from src.utils.files import Files


class CalendarDict(Dict[str, Calendar]):

    def __init__(self):
        super().__init__()
        self.load_from_file()

    def load_from_file(self):
        for name, calendar in File.read_json(Files.calendars).items():
            self[name] = jsonpickle.decode(json.dumps(calendar))

    def load_from_google(self):
        calendars = GoogleCalAPI.get_calendars()
        for calendar_name, calendar_id in calendars.items():
            if not any(calendar_name.endswith(x) for x in ['larry', 'shared']):
                self[calendar_name] = Calendar(calendar_name, calendars)
        self.export_to_file()

    def export_to_file(self):
        File.write_json(
            contents={name: json.loads(jsonpickle.encode(calendar)) for name, calendar in self.items()},
            path=Files.calendars
        )
