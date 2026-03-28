import logging
from datetime import datetime, time

from dateutil.relativedelta import relativedelta  # type: ignore

from src.connectors import GoogleCalAPI, TraktAPI
from src.data import Data
from src.enums import Owner
from src.models.watch import Watch
from src.utils import Input

from .media import MediaScript


class AddToCalendar(MediaScript):
    def __init__(self, start: datetime | None = None, days: int | None = None):
        super().__init__()

        if start is None:
            start_day = Input.get_date_input("Start")
            start = datetime.combine(start_day, time.min)
        if not days:
            days = Input.get_int_input("Days", input_type="#days")

        self.start = start + relativedelta(hours=4)
        self.end = self.start + relativedelta(days=days)
        self.owner = Owner.USER
        self.location = Data.geo_location_dict["home"]

    def run(self) -> None:
        events = GoogleCalAPI.get_events(self.calendar, self.owner, 1000, self.start, self.end)
        for event in events:
            GoogleCalAPI.delete_event(self.calendar.get_cal_id(self.owner), event.event_id)

        watches: list[Watch] = []

        movie_history = TraktAPI.get_history_for_movies(self.start, self.end)
        movie_history = sorted(movie_history, key=lambda x: x.watched_at)
        watches += self.get_watches_from_movie_history(movie_history)

        episode_history = TraktAPI.get_history_for_episodes(self.start, self.end)
        episode_history = sorted(episode_history, key=lambda x: x.watched_at)
        watches += self.get_watches_from_episode_history(episode_history)

        for watch in watches:
            logging.info(watch.__str__())
            self.create_watch_event(self.calendar, self.owner, watch, self.location)
