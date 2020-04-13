from datetime import datetime

from dateutil import tz
from dateutil.relativedelta import relativedelta

from src.scripts.script import Media
from src.connectors.trakt import TraktAPI
from src.models.watch import EpisodeWatch, TempEpisodeWatch
from src.utils.input import Input
from src.utils.output import Output

TODAY = datetime(datetime.now().year, datetime.now().month, datetime.now().day)


class UpdatePeriod(Media):

    def __init__(self, start: datetime = None, days: int = None):
        super().__init__()

        if not start:
            start = Input.get_date_input('Start')
        if not days:
            days = Input.get_int_input('Days', input_type='#days')

        self.start = start + relativedelta(hours=4)
        self.end = self.start + relativedelta(days=int(days))

        self.owner = Input.get_string_input('Calendar owner', input_type='name', default=self.owner)
        self.location = Input.get_string_input('Location', input_type='name', default=self.location)
        self.gap = Input.get_int_input('Maximum gap', input_type='#min', default=self.gap)

    def run(self):
        Output.make_title('Processing')

        history = sorted(TraktAPI.get_history(self.start, self.end), key=lambda x: x.get('watched_at'))
        watches = self.utils.get_watches_from_history(history)
        self.utils.process_watches(watches, self.calendar.__getattribute__(self.owner), self.location, self.gap)

        Output.make_bold('Updated trakt history\n')


class UpdateToday(UpdatePeriod):

    def __init__(self):
        today = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
        super().__init__(start=today, days=1)


class UpdateYesterday(UpdatePeriod):

    def __init__(self):
        yesterday = datetime(datetime.now().year, datetime.now().month, datetime.now().day) - relativedelta(days=1)
        super().__init__(start=yesterday, days=1)


class AddToHistory(Media):

    def __init__(self):
        super().__init__()

        self.show_title = Input.get_string_input('Show', 'title')
        self.season = Input.get_int_input('Season', 'no')
        self.first_episode = Input.get_int_input('First episode', 'no')
        self.last_episode = Input.get_int_input('Last episode', 'no', self.first_episode)
        self.start = Input.get_date_time_input('Start')
        self.time_zone = Input.get_string_input('Time zone', 'name', self.time_zone)
        self.owner = Input.get_string_input('Calendar owner', input_type='name', default=self.owner)
        self.location = Input.get_string_input('Location', 'name', self.location)
        self.gap = Input.get_int_input('Gap', '#min', self.gap)

    def run(self):
        Output.make_title('Processing')

        start = self.start.replace(tzinfo=tz.gettz(self.time_zone))
        show = TraktAPI.get_show_details(self.show_title)
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

        self.utils.process_watches(watches, self.calendar.__getattribute__(self.owner), self.location, self.gap)

        Output.make_bold('Added to history\n')
