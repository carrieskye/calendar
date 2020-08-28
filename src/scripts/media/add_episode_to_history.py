from dateutil import tz
from dateutil.relativedelta import relativedelta

from src.connectors.trakt import TraktAPI
from src.models.watch import EpisodeWatch, TempEpisodeWatch
from src.scripts.media.media import MediaScript
from src.utils.input import Input
from src.utils.logger import Logger


class AddEpisodesToHistory(MediaScript):

    def __init__(self):
        super().__init__()

        self.show_title = Input.get_string_input('Show', 'title')
        self.first_season = Input.get_int_input('First season', 'no')
        self.first_episode = Input.get_int_input('First episode', 'no')
        self.last_season = Input.get_int_input('Last season', 'no', self.first_season)
        self.last_episode = Input.get_int_input('Last episode', 'no', self.first_episode)
        self.start = Input.get_date_time_input('Start')
        spread = Input.get_bool_input('Spread')
        self.end = Input.get_date_time_input('End', default=self.start) if spread else self.start
        self.owner = self.get_owner()
        self.location = self.get_location()

    def run(self):
        Logger.sub_title('Processing')

        start = self.start.replace(tzinfo=tz.gettz(self.location.time_zone))
        show = TraktAPI.get_show_details(self.show_title)
        show_id = show.get('ids').get('trakt')
        watches = []
        episodes = {}

        if self.first_season == self.last_season:
            episodes[self.first_season] = range(self.first_episode, self.last_episode + 1)
        else:
            season_details = TraktAPI.get_season_details(show_id, self.first_season)
            episodes[self.first_season] = range(self.first_episode, len(season_details) + 1)
            for season in range(self.first_season + 1, self.last_season):
                season_details = TraktAPI.get_season_details(show_id, season)
                episodes[season] = range(1, len(season_details) + 1)
            episodes[self.last_season] = range(1, self.last_episode + 1)

        for season_no, episode_range in episodes.items():
            for episode_no in episode_range:
                details = self.get_episode_details(show_id, str(season_no), str(episode_no))
                temp_watch = TempEpisodeWatch(
                    watched_at=start + relativedelta(minutes=details['runtime']),
                    show_id=show_id,
                    show_title=self.show_title,
                    season_no=season_no,
                    episode_no=episode_no,
                    episode_id=details['trakt_id'],
                    episode_title=details['title'],
                    slug=show['ids']['slug']
                )
                watch = EpisodeWatch(temp_watch, details['runtime'])
                start += relativedelta(minutes=details['runtime'])
                watches.append(watch)
                Logger.log(watch.__str__())

        if self.end:
            watches = self.spread_watches(watches, self.end - self.start)

        self.process_watches(watches, self.calendar, self.owner, self.location)
