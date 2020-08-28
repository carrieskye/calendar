from dateutil import tz
from dateutil.relativedelta import relativedelta

from src.connectors.trakt import TraktAPI
from src.models.watch import TempMovieWatch, MovieWatch
from src.scripts.media.media import MediaScript
from src.utils.input import Input
from src.utils.logger import Logger


class AddMovieToHistory(MediaScript):

    def __init__(self):
        super().__init__()

        self.movie_title = Input.get_string_input('Movie', 'title')
        self.start = Input.get_date_time_input('Start')
        self.owner = self.get_owner()
        self.location = self.get_location()

    def run(self):
        Logger.sub_title('Processing')

        start = self.start.replace(tzinfo=tz.gettz(self.location.time_zone))
        movie = TraktAPI.search_movie(self.movie_title)
        details = TraktAPI.get_movie(movie.get('ids').get('trakt'))

        temp_watch = TempMovieWatch(
            watched_at=start + relativedelta(minutes=details['runtime']),
            movie_id=movie.get('ids').get('trakt'),
            movie_title=self.movie_title,
            slug=movie.get('ids').get('slug'),
            year=details['year']
        )
        watches = [MovieWatch(temp_watch, details['runtime'])]
        Logger.log(watches[0].__str__())
        self.process_watches(watches, self.calendar, self.owner, self.location)
