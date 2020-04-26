from dateutil import tz
from dateutil.relativedelta import relativedelta

from src.connectors.trakt import TraktAPI
from src.models.watch import TempMovieWatch, MovieWatch
from src.scripts.script import Media
from src.utils.input import Input
from src.utils.media import MediaUtils
from src.utils.output import Output


class AddMovieToHistory(Media):

    def __init__(self):
        super().__init__()

        self.movie_title = Input.get_string_input('Movie', 'title')
        self.start = Input.get_date_time_input('Start')
        self.owner = self.get_owner()
        self.location = self.get_location()
        self.gap = Input.get_int_input('Gap', '#min', self.gap)

    def run(self):
        Output.make_title('Processing')

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
        MediaUtils.process_watches(watches, self.calendar.get_cal_id(self.owner), self.location, self.gap)
        Output.make_bold('Added to history\n')