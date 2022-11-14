import logging
from collections import defaultdict
from pathlib import Path

from dateutil.relativedelta import relativedelta
from skye_comlib.utils.file import File
from skye_comlib.utils.formatter import Formatter

from src.models.activity import Activities, Activity
from src.models.calendar import Owner
from src.scripts.activity.activity import ActivityScript


class ParseTimingExportScript(ActivityScript):
    def __init__(self):
        super().__init__()

        self.location = self.get_location()

    def run(self):
        super().run()

        for owner in [Owner.carrie]:
            logging.info(Formatter.sub_title(owner.name))

            export = File.read_csv(Path(f"data/activity/{owner.name}/All Activities.csv"))

            all_activities = Activities()
            for item in export:
                if item["Project"].split(" ▸ ")[0].lower() == "todo":
                    continue
                activity = Activity.from_dict(item, self.location.time_zone, owner)
                if activity.location and "short" not in activity.location.__dict__:
                    raise Exception(f"No short for {activity.location.address}")
                all_activities.append(activity)

            activities_per_day = defaultdict(Activities)
            for activity in all_activities:
                start_day = (activity.start.date_time - relativedelta(hours=4)).strftime("%Y-%m-%d")
                if not activities_per_day[start_day]:
                    previous_day = (activity.start.date_time - relativedelta(days=1, hours=4)).strftime("%Y-%m-%d")
                    if previous_day in activities_per_day.keys():
                        last_activity = activities_per_day[previous_day][-1]
                        last_activity_end = last_activity.end.date_time
                        if last_activity_end + relativedelta(minutes=20) > activity.start.date_time:
                            if last_activity.title == activity.title:
                                activities_per_day[previous_day].append(activity)
                                continue
                activities_per_day[start_day].append(activity)

            for day, activities in activities_per_day.items():
                activities.merge_short_activities(default_location=self.location)
                activities.remove_double_activities()

                dir_name = Path(f"data/activity/{owner.name}")
                File.write_csv([x.flatten() for x in activities], dir_name / f"csv/{day}.csv")
                File.write_json_pickle(activities, dir_name / f"json/{day}.json")
                logging.info(f"Processed [bold]{day}", extra={"markup": True})

            logging.info(f"\n[bold pale_green3]Processed {len(activities_per_day)} days.", extra={"markup": True})
