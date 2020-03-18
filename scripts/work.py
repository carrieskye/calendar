from datetime import datetime, time

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
        days = Input.get_int_input('Days', '#days')
        self.end = self.day + relativedelta(days=days - 1)
        self.project = Input.get_string_input('Project', default='CSET')
        self.skating = Input.get_bool_input('Skating')

        self.addresses = {
            'Viola': 'Viola Arena, Olympian Dr, Cardiff CF11 0JS, UK',
            'Tramshed': 'Tramshed Tech, Pendyris St, Cardiff, UK'
        }

    def run(self):
        Output.make_title('Processing')

        while self.day <= self.end:
            if self.day.weekday() == 7 or self.day.weekday() < 5:
                if self.skating:
                    self.create_event(self.cal_id_sports, 'Ice skating', 'Viola', '', time(8), time(9))

                self.create_event(self.cal_id_work, 'Amplyfi', 'Tramshed', self.project, time(10), time(12, 30))
                self.create_event(self.cal_id_work_larry, 'Amplyfi', 'Tramshed', '', time(10), time(12, 30))

                self.create_event(self.cal_id_food, 'Lunch', 'Tramshed', '', time(12, 30), time(13, 30))

                self.create_event(self.cal_id_work, 'Amplyfi', 'Tramshed', self.project, time(13, 30), time(17))
                self.create_event(self.cal_id_work_larry, 'Amplyfi', 'Tramshed', '', time(13, 30), time(17))

            self.day += relativedelta(days=1)

        Output.make_bold('Added work days\n')

    def create_event(self, cal_id: str, summary: str, location: str, description: str, start: time, end: time):
        event = Event(
            summary=summary,
            location=self.addresses[location],
            description=description,
            start=EventDateTime(
                date_time=self.day + relativedelta(hours=start.hour, minutes=start.minute),
                time_zone=self.time_zone),
            end=EventDateTime(
                date_time=self.day + relativedelta(hours=end.hour, minutes=end.minute),
                time_zone=self.time_zone)
        )
        self.google_cal.create_event(cal_id, event)


class UpdateProject(Work):

    def __init__(self):
        super(UpdateProject, self).__init__()

        Output.make_title('Input')
        self.start = Input.get_date_input('Start')
        days = Input.get_int_input('Days', '#days')
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

        start = Input.get_date_input('Start')
        self.start = datetime.combine(start, time(4, 0))
        days = Input.get_int_input('Days', '#days')
        self.end = self.start + relativedelta(days=days)

    def run(self):
        Output.make_title('Processing')

        print(self.cal_id_work_larry)
        print(self.start)
        print(self.end)

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
