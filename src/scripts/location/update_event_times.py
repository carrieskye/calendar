import operator
from datetime import datetime, time

from dateutil.relativedelta import relativedelta

from src.models.calendar import Owner
from src.models.location_event import LocationEvent
from src.models.location_event_temp import LocationEventTemp
from src.scripts.location.location import Location
from src.utils.input import Input
from src.utils.table_print import TablePrint


class UpdateEventTimes(Location):

    def __init__(self):
        super(UpdateEventTimes, self).__init__()

        self.owner = self.get_owner(default=Owner.carrie)
        yesterday = (datetime.now() - relativedelta(days=1)).date()
        start = Input.get_date_input('Date', min_date=datetime(2019, 11, 20).date(), default=yesterday)
        self.start = datetime.combine(start, time(4, 0))
        self.end = self.start + relativedelta(days=1)

    def run(self):
        headers = ['TIME', 'LAT - LON', 'ACCURACY', 'LOCATION']
        table_print = TablePrint('Processing events', headers, [8, 25, 10, 30])
        results = self.get_records(self.start, self.end, self.owner)
        locations = [LocationEvent.from_database(result) for result in results]
        locations = sorted(locations, key=operator.attrgetter('date_time'))

        event_start = locations[0].date_time
        current_location = None
        events = []
        for location in locations:
            closest_location = self.get_closest_location(location)
            date_time = location.date_time.strftime('%H:%M:%S')
            values = [date_time, f'{location.latitude}, {location.longitude}', location.accuracy, closest_location]
            table_print.print_line(values)

            if not current_location and closest_location:
                current_location = LocationEventTemp(closest_location, [closest_location], event_start)
            elif current_location:
                label = closest_location if closest_location else 'unknown'
                if current_location.name != label or location == locations[-1]:
                    current_location.end = location.date_time
                    events.append(current_location)
                    event_start = location.date_time
                    current_location = LocationEventTemp(label, [closest_location], event_start)
                else:
                    current_location.events.append(closest_location)

        self.print_events('Determining closest location', events)
        self.group_events(events)
