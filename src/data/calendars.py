from pathlib import Path

from src.connectors import GoogleCalAPI
from src.models.calendar import Calendar
from src.utils import File


class CalendarDict(dict[str, Calendar]):
    calendar_file = Path("data/calendars.json")

    def __init__(self) -> None:
        super().__init__()
        self.load_from_file()

    def load_from_file(self) -> None:
        raw = File.read_json(self.calendar_file)
        if not isinstance(raw, dict):
            return
        for name, calendar in raw.items():
            self[name] = Calendar.model_validate(calendar)

    def load_from_google(self) -> None:
        calendars = GoogleCalAPI.get_calendars()
        for calendar_name in calendars.keys():
            if not any(calendar_name.endswith(x) for x in ["partner"]):
                self[calendar_name] = Calendar.from_key(calendar_name, calendars)
        self.export_to_file()

    def export_to_file(self) -> None:
        File.write_json(
            contents={name: calendar.model_dump(mode="json") for name, calendar in self.items()},
            path=self.calendar_file,
        )
