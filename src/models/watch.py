from datetime import timedelta

from src.utils import Utils


class Watch:

    def __init__(self, trakt_id, title, summary, details):
        self.trakt_id = trakt_id
        self.title = title
        self.end = Utils.trakt_datetime(summary.get('watched_at'))
        self.runtime = details.get('runtime')

    def get_start(self):
        return self.end - timedelta(seconds=60 * self.runtime)


class EpisodeWatch(Watch):

    def __init__(self, summary, details):
        show_id = summary.get('show').get('ids').get('trakt')
        show_title = summary.get('show').get('title')
        Watch.__init__(self, show_id, show_title, summary, details)

        self.season_no = summary.get('episode').get('season')
        self.episode_id = summary.get('episode').get('ids').get('trakt')
        self.episode_title = details.get('title')
        self.episode_no = summary.get('episode').get('number')

    def get_title(self):
        return f'S{str(self.season_no).rjust(2, "0")}E{str(self.episode_no).rjust(2, "0")} {self.episode_title}'


class MovieWatch(Watch):

    def __init__(self, summary, details):
        movie_id = summary.get('movie').get('ids').get('trakt')
        movie_title = f'{summary.get("movie").get("title")} ({details.get("year")})'
        Watch.__init__(self, movie_id, movie_title, summary, details)

        self.year = details.get('year')
