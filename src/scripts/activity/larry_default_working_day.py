from pathlib import Path

from dateutil.relativedelta import relativedelta  # type: ignore
from skye_comlib.utils.file import File
from skye_comlib.utils.input import Input

from src.scripts.activity.activity_script import ActivityScript


class LarryDefaultWorkingDayScript(ActivityScript):
    def __init__(self) -> None:
        super().__init__()
        self.start = Input.get_date_input("Start")
        days = Input.get_int_input("Days", "#days")
        self.end = self.start + relativedelta(days=days)

        self.location = self.get_location()

    def run(self) -> None:
        super().run()

        activities = []
        day = self.start
        while day < self.end:
            activities.append(
                {
                    "ID": "",
                    "Start Date": f"{day}T09:00:00Z",
                    "End Date": f"{day}T12:00:00Z",
                    "Project": "Work",
                    "Title": "Delio",
                    "Notes": "",
                },
            )
            activities.append(
                {
                    "ID": "",
                    "Start Date": f"{day}T13:00:00Z",
                    "End Date": f"{day}T18:00:00Z",
                    "Project": "Work",
                    "Title": "Delio",
                    "Notes": "",
                },
            )
            day += relativedelta(days=1)

        File.write_csv(activities, Path("data/activity/larry/All activities.csv"))
