from datetime import datetime, time

from dateutil.relativedelta import relativedelta
from skye_comlib.utils.input import Input

from src.models.calendar import Owner
from src.models.location_event import LocationEvents
from src.scripts.location.location import LocationScript


class UpdateEventTimes(LocationScript):
    def __init__(self):
        super(UpdateEventTimes, self).__init__()

        self.owner = self.get_owner(default=Owner.carrie)
        yesterday = (datetime.now() - relativedelta(days=1)).date()
        start = Input.get_date_input("Date", min_date=datetime(2019, 11, 20).date(), default=yesterday)
        self.start = datetime.combine(start, time(4, 0))
        self.end = self.start + relativedelta(days=1)

    def run(self):
        location_timestamps = self.get_location_timestamps(self.start, self.end, self.owner)
        location_timestamps.filter_incorrect_locations()

        location_events = LocationEvents.from_location_timestamps(location_timestamps)
        location_events.merge_events()
        location_events.remove_short_events()
