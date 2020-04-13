from datetime import datetime

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from src.scripts.script import Script
from src.utils.takeout import TakeoutUtils
from src.utils.utils import Utils


class SplitByDay(Script):

    def run(self):
        start_date = None
        day_locations = []
        locations = Utils.read_json('data/location_history/takeout.json').get('locations')
        for location in locations:
            date = datetime.fromtimestamp(int(location.get('timestampMs')) / 1000)
            if not start_date:
                date_as_day = parse(date.strftime('%Y-%m-%d'))
                start_date = date_as_day + relativedelta(days=1) + relativedelta(hours=4)
            if date < start_date and location != locations[-1]:
                day_locations.append(location)
            else:
                path = TakeoutUtils.get_path(start_date - relativedelta(days=1))
                Utils.write_json(day_locations, path)
                day_locations = []
                start_date = start_date + relativedelta(days=1)


class SplitByDayFormatted(Script):

    def run(self):
        start_date = None
        day_locations = []
        locations = Utils.read_json('takeout.json').get('locations')

        for location in locations:
            date, compact_location = TakeoutUtils.get_date_and_compact_location(location)
            if not start_date:
                date_as_day = parse(date.strftime('%Y-%m-%d'))
                start_date = date_as_day + relativedelta(days=1) + relativedelta(hours=4)
            if date < start_date:
                day_locations.append(compact_location)
            else:
                path = TakeoutUtils.get_path(start_date - relativedelta(days=1))
                Utils.write_json(day_locations, path)
                day_locations = []
                start_date = start_date + relativedelta(days=1)
