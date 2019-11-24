import re
import sys
from datetime import datetime
from distutils.util import strtobool
from typing import List

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalendarAPI
from src.models.event import Event
from src.utils.nice_print import NicePrint
from src.utils.utils import Utils


class Clean:

    @staticmethod
    def clean_old_events(items: int, start: datetime, end: datetime, calendars: str):
        calendars = GOOGLE_CALENDAR_API.get_calendars_from_string(calendars)

        headers = ['SUMMARY', 'LOCATION', 'DESCRIPTION', 'START', 'END', 'TZ START', 'TZ END', 'UPDATED']
        lengths = [40, 60, 40, 10, 10, 16, 16, 10]

        for calendar_name, calendar_id in calendars.items():
            if start >= datetime(2018, 1, 1) or 'larry' not in calendar_name:
                nice_print = NicePrint(calendar_name, headers, lengths)
                results = GOOGLE_CALENDAR_API.get_events(calendar_id, items, start, end)
                for result in results:
                    event = Event.get_event(result, calendar_name)
                    old_event = event.to_dict().copy()

                    event.update_summary()
                    event.update_location_and_description()
                    event.update_start_and_end()

                    if '</b><br>' in event.description:
                        description = event.description.strip('<b>')
                        subject, location = description.split('</b><br>')
                        event.description = f'{location} ({subject[0].lower() + subject[1:]})'

                    if not event.location and '>' in event.description and 'transport' not in calendar_name:
                        Clean.move_transport(calendar_name, calendar_id, event)

                    if result.get('recurringEventId'):
                        GOOGLE_CALENDAR_API.create_event(calendar_id, event)
                        Print.print_event(nice_print, event, '', 'NEW')
                    elif Event.equals(event.to_dict(), old_event):
                        GOOGLE_CALENDAR_API.update_event(calendar_id, event.event_id, event)
                        Print.print_event(nice_print, event, '', 'UPDATED')
                    else:
                        Print.print_event(nice_print, event, '', ' ')

    @staticmethod
    def move_transport(calendar_name: str, calendar_id: str, event: Event):
        owner = re.sub(r'(.*?)_', '_', calendar_name) if '_' in calendar_name else ''
        destination_name = f'transport{owner}'
        destination = GOOGLE_CALENDAR_API.calendars[destination_name]
        GOOGLE_CALENDAR_API.move_event(calendar_id, event.event_id, destination)


class Print:

    @staticmethod
    def sort_events(events: List[Event], sort_by: List[str]):
        return sorted(events, key=lambda x: tuple(Utils.get_recursive_attr(x, val) for val in sort_by))

    @staticmethod
    def print_event(nice_print: NicePrint, event: Event, calendar_name: str, updated: str):
        summary = event.summary
        location = event.location if event.location or '>' not in event.description else ''.join(['='] * 60)
        description = event.description
        start = event.start.date_time.strftime('%d %m %Y') if event.start.date_time else ''
        end = event.end.date_time.strftime('%d %m %Y') if event.end else ''
        start_tz = event.start.time_zone if event.start.time_zone else ''
        end_tz = event.end.time_zone if event.end.time_zone else ''

        line = [calendar_name] if calendar_name else []
        line += [summary, location, description, start, end, start_tz, end_tz]
        line += [updated] if updated else []
        nice_print.print_line(line)

    @staticmethod
    def print_history(items: int, start: datetime, end: datetime, calendars: str, sort_by: List[str], split_cal: bool,
                      larry: bool):
        calendars = GOOGLE_CALENDAR_API.get_calendars_from_string(calendars)

        if split_cal:
            Print.print_history_per_calendar(items, start, end, calendars, sort_by, larry)
        else:
            Print.print_history_together(items, start, end, calendars, sort_by, larry)

    @staticmethod
    def print_history_per_calendar(items: int, start: datetime, end: datetime, calendars: dict, sort_by: List[str],
                                   larry: bool):
        headers = ['SUMMARY', 'LOCATION', 'DESCRIPTION', 'START', 'END', 'TZ START', 'TZ END']
        lengths = [40, 60, 40, 10, 10, 16, 16]

        for calendar_name, calendar_id in calendars.items():
            if calendar_name in calendars:
                if larry or 'larry' not in calendar_name:
                    results = GOOGLE_CALENDAR_API.get_events(calendar_id, items, start, end)
                    events = [Event.get_event(result, calendar_name) for result in results]
                    if sort_by:
                        events = Print.sort_events(events, sort_by)
                    nice_print = NicePrint(calendar_name, headers, lengths)

                    for event in events:
                        Print.print_event(nice_print, event, '', '')

    @staticmethod
    def print_history_together(items: int, start: datetime, end: datetime, calendars: dict, sort_by: List[str],
                               larry: bool):
        headers = ['CALENDAR', 'SUMMARY', 'LOCATION', 'DESCRIPTION', 'START', 'END', 'TZ START', 'TZ END']
        lengths = [20, 40, 60, 40, 10, 10, 16, 16]

        all_events = []
        for calendar_name, calendar_id in calendars.items():
            if larry or 'larry' not in calendar_name:
                results = GOOGLE_CALENDAR_API.get_events(calendar_id, items, start, end)
                all_events += [Event.get_event(result, calendar_name) for result in results]

        if sort_by:
            all_events = Print.sort_events(all_events, sort_by)

        nice_print = NicePrint('EVENTS', headers, lengths)

        for event in all_events:
            Print.print_event(nice_print, event, event.calendar, '')


GOOGLE_CALENDAR_API = GoogleCalendarAPI()

CURRENT_YEAR = str(datetime.now().year)
CURRENT_MONTH = str(datetime.now().month)
CURRENT_WEEK_NO = datetime.now().strftime('%V')


def clean_week(year=CURRENT_YEAR, week=CURRENT_WEEK_NO, calendars='all'):
    start = datetime.strptime(f'{year}-W{week}' + '-1', "%Y-W%W-%w")
    end = start + relativedelta(weeks=1)
    Clean.clean_old_events(100, start, end, calendars)


def clean_month(year=CURRENT_YEAR, month=CURRENT_MONTH, calendars='all'):
    start = datetime(int(year), int(month), 1)
    end = start + relativedelta(months=1)
    Clean.clean_old_events(1000, start, end, calendars)


def clean_year(year=CURRENT_YEAR, calendars='all'):
    start = datetime(int(year), 1, 1)
    end = start + relativedelta(years=1)
    Clean.clean_old_events(10000, start, end, calendars)


def print_history_year(year=CURRENT_YEAR, calendars='all', sort_by='start.date_time', split_cal='true', larry='true'):
    GOOGLE_CALENDAR_API.update_calendar_dict()
    start = datetime(int(year), 1, 1)
    end = start + relativedelta(years=1)
    sort_by = sort_by.split(',') if sort_by else []
    Print.print_history(10000, start, end, calendars, sort_by, strtobool(split_cal), strtobool(larry))


def print_full_history(calendars='all', sort_by='start.date_time', split_cal='true', larry='true'):
    start = datetime(2012, 1, 1)
    end = datetime.now()
    sort_by = sort_by.split(',') if sort_by else []
    Print.print_history(10000, start, end, calendars, sort_by, strtobool(split_cal), strtobool(larry))


def print_history_as_of(start: str, calendars='all', sort_by='start.date_time', split_cal='true', larry='true'):
    start = parse(start)
    end = datetime(int(CURRENT_YEAR), 12, 31)
    sort_by = sort_by.split(',') if sort_by else []
    Print.print_history(10000, start, end, calendars, sort_by, strtobool(split_cal), strtobool(larry))


if __name__ == '__main__':
    if len(sys.argv) > 2:
        globals()[sys.argv[1]](*sys.argv[2:])
    else:
        globals()[sys.argv[1]]()
