import json
from collections import defaultdict

import jsonpickle
from dateutil.relativedelta import relativedelta

from src.models.activity import Activities, Activity
from src.models.calendar import Owner
from src.scripts.script import Work
from src.utils.file import File
from src.utils.logger import Logger


class ParseTimingExportScript(Work):

    def __init__(self):
        super().__init__()

        self.location = self.get_location()

    def run(self):
        super().run()

        for owner in [Owner.carrie, Owner.larry]:
            Logger.sub_sub_title(owner.name)

            export = File.read_csv(f'data/activity/{owner.name}/All Activities.csv', log=False)

            activities_per_day = defaultdict(Activities)
            for item in export:
                if item['Project'].split(' ▸ ')[0].lower() == 'todo':
                    continue
                activity = Activity.from_dict(item, self.location.time_zone, owner)
                day = (activity.start.date_time - relativedelta(hours=5)).strftime('%Y-%m-%d')
                activities_per_day[day].append(activity)

            for day, activities in activities_per_day.items():
                activities.merge_short_activities()
                activities.remove_double_activities()
                activities.standardise_short_activities()

                file_name = f'data/activity/{owner.name}/csv/{day}'
                File.write_csv([x.flatten() for x in activities], f'{file_name}.csv', log=False)
                File.write_json(json.loads(jsonpickle.encode(activities)), f'{file_name}.json', log=False)
                Logger.log(f'Processed {day}')
