from dateutil import tz
from dateutil.relativedelta import relativedelta

from src.connectors.trakt import TraktAPI
from src.models.watch import EpisodeWatch, TempEpisodeWatch
from src.scripts.script import Media
from src.utils.input import Input
from src.utils.media import MediaUtils
from src.utils.output import Output


class AddToHistory(Media):

    def __init__(self):
        super().__init__()

        self.show_title = Input.get_string_input('Show', 'title')
        self.season = Input.get_int_input('Season', 'no')
        self.first_episode = Input.get_int_input('First episode', 'no')
        self.last_episode = Input.get_int_input('Last episode', 'no', self.first_episode)
        self.start = Input.get_date_time_input('Start')
        self.owner = self.get_owner()
        self.location = self.get_location()
        self.gap = Input.get_int_input('Gap', '#min', self.gap)

    def run(self):
        Output.make_title('Processing')

        start = self.start.replace(tzinfo=tz.gettz(self.location.time_zone))
        show = TraktAPI.get_show_details(self.show_title)
        show_id = show.get('ids').get('trakt')
        watches = []
        for episode_index in range(self.first_episode, self.last_episode + 1):
            details = MediaUtils.get_episode_details(show_id, self.season, str(episode_index))
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

        MediaUtils.process_watches(watches, self.calendar.get_cal_id(self.owner), self.location, self.gap)

        Output.make_bold('Added to history\n')
