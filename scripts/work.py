from dateutil.relativedelta import relativedelta

from scripts.script import Work
from src.models.event import Event
from src.models.event_datetime import EventDateTime
from src.utils.input import Input
from src.utils.output import Output


class AddDays(Work):
    def __init__(self):
        super(AddDays, self).__init__()

        self.day = Input.get_date_input('Start')
        days = Input.get_int_input('Days')
        self.end = self.day + relativedelta(days=days - 1)
        self.project = Input.get_string_input('Project', 'CSET')

    def run(self):
        Output.make_title('Processing')

        while self.day <= self.end:
            if self.day.weekday() == 7 or self.day.weekday() < 5:
                skating = Event(
                    summary='Ice skating',
                    location='Viola Arena, Olympian Dr, Cardiff CF11 0JS, UK',
                    description='',
                    start=EventDateTime(
                        date_time=self.day + relativedelta(hours=8), time_zone=self.time_zone),
                    end=EventDateTime(
                        date_time=self.day + relativedelta(hours=9), time_zone=self.time_zone)
                )

                morning = Event(
                    summary='Amplyfi',
                    location='Tramshed Tech, Pendyris St, Cardiff, UK',
                    description=self.project,
                    start=EventDateTime(
                        date_time=self.day + relativedelta(hours=10), time_zone=self.time_zone),
                    end=EventDateTime(
                        date_time=self.day + relativedelta(hours=12, minutes=30), time_zone=self.time_zone)
                )

                lunch = Event(
                    summary='Lunch',
                    location='Tramshed Tech, Pendyris St, Cardiff, UK',
                    description='',
                    start=EventDateTime(
                        date_time=self.day + relativedelta(hours=12, minutes=30), time_zone=self.time_zone),
                    end=EventDateTime(
                        date_time=self.day + relativedelta(hours=13, minutes=30), time_zone=self.time_zone)
                )

                afternoon = Event(
                    summary='Amplyfi',
                    location='Tramshed Tech, Pendyris St, Cardiff, UK',
                    description=self.project,
                    start=EventDateTime(
                        date_time=self.day + relativedelta(hours=13, minutes=30), time_zone=self.time_zone),
                    end=EventDateTime(
                        date_time=self.day + relativedelta(hours=18), time_zone=self.time_zone)
                )

                self.google_cal.create_event(self.cal_id_sports, skating)
                self.google_cal.create_event(self.cal_id_work, morning)
                self.google_cal.create_event(self.cal_id_food, lunch)
                self.google_cal.create_event(self.cal_id_work, afternoon)

                morning.description = ''
                afternoon.description = ''

                self.google_cal.create_event(self.cal_id_work_larry, morning)
                self.google_cal.create_event(self.cal_id_work_larry, afternoon)

            self.day += relativedelta(days=1)

        Output.make_bold('Added work days\n')


class UpdateProject(Work):

    def __init__(self):
        super(UpdateProject, self).__init__()

        Output.make_title('Input')
        self.start = Input.get_date_input('Start')
        days = Input.get_int_input('Days')
        self.end = self.start + relativedelta(days=days)
        self.project = Input.get_string_input('Project', 'CSET')

    def run(self):
        Output.make_title('Processing')

        results = self.google_cal.get_events(self.cal_id_work, 1000, self.start, self.end)
        for result in results:
            event = Event.get_event(result, 'work')
            event.summary = 'Amplyfi'
            event.description = self.project
            self.google_cal.update_event(self.cal_id_work, event.event_id, event)

        Output.make_bold('Updated work project\n')


class CopyToLarry(Work):

    def __init__(self):
        super(CopyToLarry, self).__init__()

        Output.make_title('Input')
        self.start = Input.get_date_input('Start')
        days = Input.get_int_input('Days')
        self.end = self.start + relativedelta(days=days)

    def run(self):
        Output.make_title('Processing')

        results = self.google_cal.get_events(self.cal_id_work_larry, 1000, self.start, self.end)
        for result in results:
            event = Event.get_event(result, 'work_larry')
            self.google_cal.delete_event(self.cal_id_work_larry, event.event_id)

        results = self.google_cal.get_events(self.cal_id_work, 1000, self.start, self.end)
        for result in results:
            event = Event.get_event(result, 'work')
            event.summary = 'Amplyfi'
            event.location = 'Tramshed Tech, Pendyris St, Cardiff, UK'
            event.description = ''
            self.google_cal.create_event(self.cal_id_work_larry, event)

        Output.make_bold('Copied to Larry\n')
