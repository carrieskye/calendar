# import operator
# from datetime import datetime, time
#
# from dateutil.relativedelta import relativedelta
#
# from src.models.location_event import LocationEvent
# from src.models.location_event_temp import LocationEventTemp
# from src.scripts.script import Locations
# from src.utils.input import Input
# from src.utils.location import LocationUtils
# from src.utils.table_print import TablePrint
# from src.utils.utils import Utils
#
#
# class UpdateEventHistory(Locations):
#
#     def __init__(self):
#         super(UpdateEventHistory, self).__init__()
#
#         start = Input.get_date_input('Date')
#         self.start = datetime.combine(start, time(4, 0))
#         self.end = self.start + relativedelta(days=1)
#
#     def run(self):
#         headers = ['TIME', 'LAT - LON', 'ACCURACY', 'LOCATION']
#         table_print = TablePrint('Processing events', headers, [10, 25, 5, 30])
#         date_part = f'{self.start.year}/{self.start.month:02d}/{self.start.day:02d}'
#         results = Utils.read_json(f'data/location_history/{date_part}.json')
#
#         locations = [LocationEvent.from_google(result) for result in results]
#         locations = sorted(locations, key=operator.attrgetter('date_time'))
#
#         event_start = locations[0].date_time
#         current_location = None
#         events = []
#         for location in locations:
#             closest_location = LocationUtils.get_closest_location(location)
#             date_time = location.date_time.strftime('%H:%M:%S')
#             values = [date_time, f'{location.latitude}, {location.longitude}', location.accuracy, closest_location]
#             table_print.print_line(values)
#
#             if not current_location and closest_location:
#                 current_location = LocationEventTemp(closest_location, [closest_location], event_start)
#             elif current_location:
#                 label = closest_location if closest_location else 'unknown'
#                 if current_location.name != label or location == locations[-1]:
#                     current_location.end = location.date_time
#                     events.append(current_location)
#                     event_start = location.date_time
#                     current_location = LocationEventTemp(label, [closest_location], event_start)
#                 else:
#                     current_location.events.append(closest_location)
#
#         LocationUtils.print_events('Determining closest location', events)
#         group_events = LocationUtils.group_events(events)
#
#         LocationUtils.process_events(self.start.date(), group_events, False)
