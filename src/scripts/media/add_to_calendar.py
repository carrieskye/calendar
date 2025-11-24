import logging
from datetime import datetime
from typing import List, Optional

from dateutil.relativedelta import relativedelta  # type: ignore
from skye_comlib.utils.input import Input

from src.connectors.google_calendar import GoogleCalAPI
from src.connectors.trakt import TraktAPI
from src.data.data import Data
from src.models.calendar import Owner
from src.models.watch import Watch
from src.scripts.media.media import MediaScript


class AddToCalendar(MediaScript):
    def __init__(self, start: Optional[datetime] = None, days: Optional[int] = None):
        super().__init__()

        if not start:
            start = Input.get_date_input("Start")
        if not days:
            days = Input.get_int_input("Days", input_type="#days")

        self.start = start + relativedelta(hours=4)
        self.end = self.start + relativedelta(days=days)
        self.owner = Owner.carrie
        self.location = Data.geo_location_dict["järnvägsgatan_41_orsa"]

    def run(self) -> None:
        events = GoogleCalAPI.get_events(self.calendar, self.owner, 1000, self.start, self.end)
        for event in events:
            GoogleCalAPI.delete_event(self.calendar.get_cal_id(self.owner), event.event_id)

        watches: List[Watch] = []

        movie_history = TraktAPI.get_history_for_movies(self.start, self.end)
        movie_history = sorted(movie_history, key=lambda x: x.watched_at)
        watches += self.get_watches_from_movie_history(movie_history)

        episode_history = TraktAPI.get_history_for_episodes(self.start, self.end)
        episode_history = sorted(episode_history, key=lambda x: x.watched_at)
        watches += self.get_watches_from_episode_history(episode_history)

        for watch in watches:
            logging.info(watch.__str__())
            self.create_watch_event(self.calendar, self.owner, watch, self.location)
