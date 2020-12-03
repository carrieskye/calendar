import json
from collections import defaultdict

import jsonpickle
from dateutil.relativedelta import relativedelta

from src.models.activity import Activities, Activity
from src.models.calendar import Owner
from src.scripts.activity.activity import ActivityScript
from src.utils.file import File
from src.utils.logger import Logger


class ParseTimingExportScript(ActivityScript):

    def __init__(self):
        super().__init__()

        self.location = self.get_location()

    def run(self):
        super().run()

        for owner in [Owner.carrie, Owner.larry]:
            Logger.sub_sub_title(owner.name)

            export = File.read_csv(f'data/activity/{owner.name}/All Activities.csv', log=False)

            all_activities = Activities()
            for item in export:
                if item['Project'].split(' ▸ ')[0].lower() == 'todo':
                    continue
                activity = Activity.from_dict(item, self.location.time_zone, owner)
                if activity.location and not 'short' in activity.location.__dict__:
                    raise Exception(f'No short for {activity.location.address}')
                all_activities.append(activity)

            activities_per_day = defaultdict(Activities)
            for activity in all_activities:
                start_day = (activity.start.date_time - relativedelta(hours=5)).strftime('%Y-%m-%d')
                if not activities_per_day[start_day]:
                    previous_day = (activity.start.date_time - relativedelta(days=1, hours=5)).strftime('%Y-%m-%d')
                    if previous_day in activities_per_day.keys():
                        last_activity = activities_per_day[previous_day][-1]
                        last_activity_end = last_activity.end.date_time
                        if last_activity_end + relativedelta(minutes=30) > activity.start.date_time \
                                and last_activity.title == activity.title:
                            activities_per_day[previous_day].append(activity)
                            continue
                activities_per_day[start_day].append(activity)

            for day, activities in activities_per_day.items():
                activities.merge_short_activities()
                activities.remove_double_activities()

                dir_name = f'data/activity/{owner.name}/'
                File.write_csv([x.flatten() for x in activities], f'{dir_name}/csv/{day}.csv', log=False)
                File.write_json(json.loads(jsonpickle.encode(activities)), f'{dir_name}/json/{day}.json', log=False)
                Logger.log(f'Processed {day}')
