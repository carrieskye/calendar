from datetime import datetime

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


class TempEpisodeWatch:

    def __init__(self, watched_at: datetime, show_id: str, show_title: str, season_no: int, episode_no: int,
                 episode_id: str = None, episode_title: str = None, slug: str = None):
        self.watched_at = watched_at
        self.show_id = show_id
        self.show_title = show_title
        self.season_no = season_no
        self.episode_id = episode_id
        self.episode_title = episode_title
        self.episode_no = episode_no
        self.slug = slug

    @classmethod
    def from_result(cls, result: dict):
        return cls(
            watched_at=parse(result.get('watched_at')),
            show_id=str(result.get('show').get('ids').get('trakt')),
            show_title=result.get('show').get('title'),
            season_no=result.get('episode').get('season'),
            episode_no=result.get('episode').get('number'),
            episode_id=result.get('episode').get('ids').get('trakt'),
            episode_title=result.get('episode').get('title'),
            slug=result.get('show').get('ids').get('slug')
        )


class TempMovieWatch:

    def __init__(self, watched_at: datetime, movie_id: str, movie_title: str = None, slug: str = None,
                 year: int = None):
        self.watched_at = watched_at
        self.movie_id = movie_id
        self.movie_title = movie_title
        self.slug = slug
        self.year = year

    @classmethod
    def from_result(cls, result: dict):
        return cls(
            watched_at=parse(result.get('watched_at')),
            movie_id=result.get('movie').get('ids').get('trakt'),
            movie_title=result.get('movie').get('title'),
            slug=result.get('movie').get('ids').get('slug'),
            year=result.get('movie').get('year')
        )


class Watch:

    def __init__(self, trakt_id: str, title: str, details: dict, watched_at: datetime, runtime: int):
        self.trakt_id = trakt_id
        self.title = title
        self.details = details
        self.end = watched_at
        self.runtime = runtime

    def get_start(self):
        return self.end - relativedelta(minutes=self.runtime)


class EpisodeWatch(Watch):

    def __init__(self, temp_watch: TempEpisodeWatch, runtime: int):
        self.show_title = temp_watch.show_title
        self.season_no = temp_watch.season_no
        self.episode_id = temp_watch.episode_id
        self.episode_title = temp_watch.episode_title
        self.episode_no = temp_watch.episode_no
        self.slug = temp_watch.slug

        show_id = temp_watch.show_id
        show_title = self.show_title.replace('Marvel\'s ', '').split(' (')[0]
        watched_at = temp_watch.watched_at
        details = {
            'url': f'https://trakt.tv/shows/{self.slug}/seasons/{self.season_no}/episodes/{self.episode_no}',
            'episode': f'S{str(self.season_no).rjust(2, "0")}E{str(self.episode_no).rjust(2, "0")}'
        }
        super().__init__(show_id, show_title, details, watched_at, runtime)

    def get_export_dict(self) -> dict:
        return {
            'season': self.season_no,
            'episode': self.episode_no,
            'title': self.episode_title,
            'start': self.get_start().strftime('%Y-%m-%d %H:%M:%S'),
            'end': self.end.strftime('%Y-%m-%d %H:%M:%S')
        }


class MovieWatch(Watch):

    def __init__(self, temp_watch: TempMovieWatch, runtime: int):
        self.movie_title = temp_watch.movie_title
        self.slug = temp_watch.slug
        self.year = temp_watch.year

        movie_id = temp_watch.movie_id
        movie_title = self.movie_title.split(':')[0]
        watched_at = temp_watch.watched_at
        details = {
            'url': f'https://trakt.tv/movies/{self.slug}',
            'year': self.year
        }
        Watch.__init__(self, movie_id, movie_title, details, watched_at, runtime)

    def get_export_dict(self):
        return {
            'title': self.movie_title,
            'year': self.year,
            'start': self.get_start().strftime('%Y-%m-%d %H:%M:%S'),
            'end': self.end.strftime('%Y-%m-%d %H:%M:%S')
        }
