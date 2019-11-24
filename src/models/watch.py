from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


class Watch:

    def __init__(self, trakt_id, title, watched_at, details):
        self.trakt_id = trakt_id
        self.title = title
        self.end = parse(watched_at)
        self.runtime = details.get('runtime')

    def get_start(self):
        return self.end - relativedelta(minutes=self.runtime)

    def get_description(self):
        return ''


class EpisodeWatch(Watch):

    def __init__(self, watched_at, show, episode):
        self.show_title = show.get('title')
        self.season_no = episode.get('season')
        self.episode_id = episode.get('ids').get('trakt')
        self.episode_title = episode.get('title')
        self.episode_no = episode.get('number')
        self.slug = show.get('ids').get('slug')
        show_id = show.get('ids').get('trakt')
        show_title = self.show_title.replace('Marvel\'s ', '').split(' (')[0]
        Watch.__init__(self, show_id, show_title, watched_at, episode)

    def get_description(self):
        text = f'S{str(self.season_no).rjust(2, "0")}E{str(self.episode_no).rjust(2, "0")} {self.episode_title}'
        url = f'https://trakt.tv/shows/{self.slug}/seasons/{self.season_no}/episodes/{self.episode_no}'
        return f'<a href="{url}">{text}</a>'


class MovieWatch(Watch):

    def __init__(self, watched_at, summary, details):
        self.movie_title = summary.get('title')
        self.slug = summary.get('ids').get('slug')
        movie_id = summary.get('ids').get('trakt')
        movie_title = self.movie_title.split(':')[0]
        Watch.__init__(self, movie_id, movie_title, watched_at, details)

        self.year = details.get('year')

    def get_description(self):
        text = f'{self.movie_title} ({self.year})'
        url = f'https://trakt.tv/movies/{self.slug}'
        return f'<a href="{url}">{text}</a>'
