from datetime import datetime

from dateutil import tz
from dateutil.relativedelta import relativedelta

from scripts.script import Media
from src.models.event import Event
from src.models.watch import EpisodeWatch, TempEpisodeWatch
from src.utils.input import Input
from src.utils.output import Output

TODAY = datetime(datetime.now().year, datetime.now().month, datetime.now().day)


class UpdatePeriod(Media):

    def __init__(self, start: datetime = None, days: int = None):
        super(UpdatePeriod, self).__init__()

        if not start and not days:
            Output.make_title('Input')

        if not start:
            start = Input.get_date_input('Start')
        if not days:
            days = Input.get_int_input('Days', input_type='#days')

        self.start = start + relativedelta(hours=4)
        self.end = self.start + relativedelta(days=int(days))

        self.calendar = Input.get_string_input('Calendar', input_type='name', default=self.calendar)
        self.location = Input.get_string_input('Location', input_type='name', default=self.location)
        self.gap = Input.get_int_input('Maximum gap', input_type='#min', default=self.gap)

    def run(self):
        Output.make_title('Processing')

        history = sorted(self.trakt_api.get_history(self.start, self.end), key=lambda x: x.get('watched_at'))
        watches = self.utils.get_watches_from_history(history)
        self.utils.process_watches(watches, self.google_cal.get_calendar_id(self.calendar), self.location, self.gap)

        Output.make_bold('Updated trakt history\n')


class UpdateToday(Media):

    def __init__(self):
        super(UpdateToday, self).__init__()

        Output.make_title('Input')
        today = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
        self.update_trakt_period = UpdatePeriod(start=today, days=1)

    def run(self):
        self.update_trakt_period.run()


class UpdateYesterday(Media):

    def __init__(self):
        super(UpdateYesterday, self).__init__()

        Output.make_title('Input')
        today = datetime(datetime.now().year, datetime.now().month, datetime.now().day) - relativedelta(days=1)
        self.update_trakt_period = UpdatePeriod(start=today, days=1)

    def run(self):
        self.update_trakt_period.run()


class AddToHistory(Media):

    def __init__(self):
        super(AddToHistory, self).__init__()

        Output.make_title('Input')
        self.show_title = Input.get_string_input('Show', 'title')
        self.season = Input.get_int_input('Season', 'no')
        self.first_episode = Input.get_int_input('First episode', 'no')
        self.last_episode = Input.get_int_input('Last episode', 'no', self.first_episode)
        self.start = Input.get_date_time_input('Start')
        self.time_zone = Input.get_string_input('Time zone', 'name', self.time_zone)
        self.calendar = Input.get_string_input('Calendar', 'name', self.calendar)
        self.location = Input.get_string_input('Location', 'name', self.location)
        self.gap = Input.get_int_input('Gap', '#min', self.gap)

    def run(self):
        Output.make_title('Processing')

        start = self.start.replace(tzinfo=tz.gettz(self.time_zone))
        show = self.trakt_api.get_show_details(self.show_title)
        show_id = show.get('ids').get('trakt')
        watches = []
        for episode_index in range(self.first_episode, self.last_episode + 1):
            details = self.utils.get_episode_details(show_id, self.season, str(episode_index))
            temp_watch = TempEpisodeWatch(
                watched_at=start + relativedelta(minutes=details['runtime']),
                show_id=show_id,
                show_title=self.show_title,
                season_no=self.season,
                episode_no=episode_index,
                episode_id=details['trakt_id'],
                episode_title=details['title']
            )
            watch = EpisodeWatch(temp_watch, details['runtime'])
            start += relativedelta(minutes=details['runtime'])
            watches.append(watch)

        self.utils.process_watches(watches, self.google_cal.get_calendar_id(self.calendar), self.location, self.gap)

        Output.make_bold('Added to history\n')


class ExportFromCalendar(Media):

    def __init__(self):
        super(ExportFromCalendar, self).__init__()

    def run(self):
        results = []
        tv_calendar_id = self.google_cal.get_calendar_id('tv')
        results += self.google_cal.get_events(tv_calendar_id, 10000, datetime(2012, 1, 1), datetime.now())

        for result in results:
            event = Event.get_event(result, tv_calendar_id, 'tv')
            self.utils.process_calendar_event(event)

        # TODO!!


class ExportFromTrakt(Media):

    def __init__(self):
        super(ExportFromTrakt, self).__init__()

    def run(self):
        results = []

        Output.make_title('Retrieving data')
        period = relativedelta(weeks=1)
        start = datetime(2013, 1, 1)
        while start < datetime.now() + 2 * period:
            end = start + period
            print(f'Retrieving {start.strftime("%Y-%m-%d")} until {end.strftime("%Y-%m-%d")}')
            results += self.trakt_api.get_history(start, end)
            start += period

        self.utils.export_history(results)
