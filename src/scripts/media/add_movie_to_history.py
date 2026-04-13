import logging

from dateutil import tz
from dateutil.relativedelta import relativedelta

from src.connectors import TraktAPI
from src.data import GeoLocations
from src.enums import Owner
from src.models import MovieWatch, TempMovieWatch, Watch
from src.utils import Input

from .media import MediaScript

logger = logging.getLogger(__name__)


class AddMovieToHistory(MediaScript):
    def __init__(self) -> None:
        super().__init__()

        self.movie_title = Input.get_string_input("Movie", "title")
        self.start = Input.get_date_time_input("Start")
        self.owner = Owner.USER
        self.location = GeoLocations.home

    def run(self) -> None:
        start = self.start.replace(tzinfo=tz.gettz(self.location.time_zone))
        movie = TraktAPI.search_movie(self.movie_title)
        details = TraktAPI.get_movie(movie.ids.trakt)

        temp_watch = TempMovieWatch(
            watched_at=start + relativedelta(minutes=details.runtime),
            movie_id=movie.ids.trakt,
            movie_title=self.movie_title,
            slug=movie.ids.slug,
            year=details.year,
        )
        watches: list[Watch] = [MovieWatch(temp_watch, details.runtime)]
        logger.info(watches[0].__str__())
        self.process_watches(watches, self.calendar, self.owner, self.location)
