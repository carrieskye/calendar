import logging
from collections import defaultdict
from datetime import timedelta
from pathlib import Path
from typing import Dict

from dateutil.relativedelta import relativedelta  # type: ignore
from skye_comlib.utils.file import File
from skye_comlib.utils.formatter import Formatter

from src.data.data import Data
from src.models.activity.activities import Activities
from src.models.activity.activity import Activity
from src.models.calendar import Owner
from src.models.timing.timing_item import TimingItem
from src.scripts.activity.activity_script import ActivityScript


class ParseTimingExportScript(ActivityScript):
    def __init__(self) -> None:
        super().__init__()

        self.location = Data.geo_location_dict["järnvägsgatan_41_orsa"]

    def run(self) -> None:
        super().run()

        for owner in [Owner.carrie]:
            logging.info(Formatter.sub_title(owner.name))

            export = File.read_csv(Path(f"data/activity/{owner.name}/All Activities.csv"))
            timing_items = [TimingItem.model_validate(item) for item in export]

            all_activities = Activities()
            for item in timing_items:
                activity = Activity.from_timing_item(timing_item=item, default_location=self.location, owner=owner)
                if activity.calendar.name == "todo":
                    continue
                if activity.location and "short" not in activity.location.__dict__:
                    raise Exception(f"No short for {activity.location.address}")
                all_activities.append(activity)

            activities_per_day: Dict[str, Activities] = defaultdict(Activities)
            for activity in all_activities:
                if icon := Data.icons_dict.get(activity.title):
                    activity.title = f"{icon} {activity.title}"
                elif activity.title.startswith("Call "):
                    activity.title = f"📞 {activity.title.replace('Call ', '')}"
                elif activity.title.startswith("Visit "):
                    activity.title = f"🏠 {activity.title.replace('Visit ', '')}"
                elif activity.title.startswith("Birthday "):
                    activity.title = f"🎂 {activity.title.replace('Birthday ', '')}"
                elif activity.title.startswith("Haircut "):
                    activity.title = f"💇 {activity.title.replace('Haircut ', '')}"
                elif " with " in activity.title:
                    what, who = activity.title.split(" with ")
                    icon = Data.icons_dict[what]
                    who = who[0].upper() + who[1:]
                    activity.title = f"{icon} {who}"
                elif activity.title.endswith(" visiting"):
                    activity.title = f"🏠 {activity.title.replace(' visiting', '')}"
                else:
                    raise Exception(f"No icon for {activity.title} - {activity.model_dump(mode='json')}")

                start_day = (activity.start.date_time - relativedelta(hours=4)).strftime("%Y-%m-%d")
                if not activities_per_day[start_day]:
                    previous_day = (activity.start.date_time - relativedelta(days=1, hours=4)).strftime("%Y-%m-%d")
                    if activities_per_day[previous_day]:
                        last_activity = activities_per_day[previous_day][-1]
                        last_activity_end = last_activity.end.date_time
                        if (
                            last_activity_end + relativedelta(minutes=20) > activity.start.date_time
                        ) and last_activity.title == activity.title:
                            activities_per_day[previous_day].append(activity)
                            continue
                activities_per_day[start_day].append(activity)

            for day, activities in activities_per_day.items():
                if not activities:
                    continue

                activities.merge_short_activities(max_time_diff=timedelta(minutes=20), default_location=self.location)
                activities.remove_double_activities()

                for activity in activities:
                    if activity.title == "🚙️ Errands":
                        if any(sub_activity.projects[0] == "Groceries" for sub_activity in activity.sub_activities):
                            activity.title = "🛒 Groceries"
                        elif any(sub_activity.projects[0] == "Shopping" for sub_activity in activity.sub_activities):
                            activity.title = "🛍️ Shopping"
                        elif any(sub_activity.projects[-1] == "Bank" for sub_activity in activity.sub_activities):
                            activity.title = "🏦 Bank"
                    if (
                        len(activity.sub_activities) == 1
                        and len(activity.sub_activities[0].projects) == 1
                        and activity.title.endswith(activity.sub_activities[0].projects[0])
                    ):
                        activity.sub_activities = []
                    for sub_activity in activity.sub_activities:
                        if len(sub_activity.projects) > 1:
                            sub_activity.projects = [x for x in sub_activity.projects if x != "Various"]
                        if len(sub_activity.projects) > 1 and activity.title.endswith(sub_activity.projects[0]):
                            sub_activity.projects.pop(0)

                dir_name = Path(f"data/activity/{owner.name}")
                File.write_csv([x.flatten() for x in activities], dir_name / f"csv/{day}.csv")
                File.write_json_pickle(activities, dir_name / f"json/{day}.json")
                logging.info(f"Processed [bold]{day}", extra={"markup": True})

            logging.info(
                f"\n[bold pale_green3]Processed {len(activities_per_day) - 1} days.",
                extra={"markup": True},
            )
