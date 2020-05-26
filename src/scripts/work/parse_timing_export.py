import json
from collections import defaultdict

import jsonpickle
from dateutil.relativedelta import relativedelta

from src.models.activity import Activities, Activity
from src.models.calendar import Owner
from src.scripts.script import Work
from src.utils.utils import Utils


class ParseTimingExportScript(Work):

    def __init__(self):
        super().__init__()

        self.location = self.get_location()
        self.owner = self.get_owner(default=Owner.carrie)

    def run(self):
        super().run()

        export = Utils.read_csv('data/activity/All Activities.csv')

        activities_per_day = defaultdict(Activities)
        for item in export:
            activity = Activity.from_dict(item, self.location.time_zone, self.owner)
            day = (activity.start.date_time - relativedelta(hours=5)).strftime('%Y-%m-%d')
            activities_per_day[day].append(activity)

        for day, activities in activities_per_day.items():
            Utils.log(f'{day}')
            activities.merge_short_activities()
            activities.remove_double_activities()
            activities.standardise_short_activities()

            Utils.write_csv([x.flatten() for x in activities], f'data/activity/{self.owner.name}/csv/{day}.csv')
            Utils.write_json(json.loads(jsonpickle.encode(activities)),
                             f'data/activity/{self.owner.name}/json/{day}.json')
