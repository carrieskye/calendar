import logging
from typing import List

from dateutil import tz  # type: ignore
from dateutil.relativedelta import relativedelta  # type: ignore
from skye_comlib.utils.input import Input

from src.connectors.trakt import TraktAPI
from src.data.data import Data
from src.models.calendar import Owner
from src.models.watch import MovieWatch, TempMovieWatch, Watch
from src.scripts.media.media import MediaScript


class AddMovieToHistory(MediaScript):
    def __init__(self) -> None:
        super().__init__()

        self.movie_title = Input.get_string_input("Movie", "title")
        self.start = Input.get_date_time_input("Start")
        self.owner = Owner.carrie
        self.location = Data.geo_location_dict["järnvägsgatan_41_orsa"]

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
        watches: List[Watch] = [MovieWatch(temp_watch, details.runtime)]
        logging.info(watches[0].__str__())
        self.process_watches(watches, self.calendar, self.owner, self.location)
