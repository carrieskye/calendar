import os
from datetime import datetime


class TakeoutUtils:

    @staticmethod
    def get_path(date: datetime):
        base_path = 'data/location_history'

        if str(date.year) not in os.listdir(base_path):
            os.mkdir(f'{base_path}/{date.year}')
        path = f'{base_path}/{date.year}'

        if f'{date.month:02d}' not in os.listdir(path):
            os.mkdir(f'{path}/{date.month:02d}')
        path = f'{path}/{date.month:02d}'

        return f'{path}/{date.day:02d}.json'

    @staticmethod
    def get_date_and_compact_location(location: dict):
        date = datetime.fromtimestamp(int(location.get('timestampMs')) / 1000)
        compact_location = {
            'date_time': date.isoformat(),
            'latitudeE7': int(location.get('latitudeE7')) / 10000000,
            'longitudeE7': int(location.get('longitudeE7')) / 10000000
        }
        for key, value in location.items():
            if key not in compact_location and key != 'activity':
                compact_location[key] = value
        if location.get('activity'):
            compact_location['activity'] = [{
                'date_time': datetime.fromtimestamp(int(activity.get('timestampMs')) / 1000).isoformat(),
                'activity': activity.get('activity')
            } for activity in location.get('activity')]
        return date, compact_location
