from datetime import datetime

from dateutil import tz
from dateutil.relativedelta import relativedelta

from scripts.script import Media
from src.models.watch import EpisodeWatch
from src.utils.input import Input
from src.utils.media import MediaUtils
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
        watches = MediaUtils().get_watches_from_history(history)
        MediaUtils().process_watches(watches, self.google_cal.get_calendar_id(self.calendar), self.location, self.gap)

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
            episode = self.trakt_api.get_episode(show_id, self.season, episode_index)
            watch = EpisodeWatch(
                watched_at=(start + relativedelta(minutes=episode.get('runtime'))).isoformat(),
                show=show,
                episode=episode)
            start += relativedelta(minutes=episode.get('runtime'))
            watches.append(watch)

        MediaUtils().process_watches(watches, self.google_cal.get_calendar_id(self.calendar), self.location, self.gap)

        Output.make_bold('Added to history\n')
