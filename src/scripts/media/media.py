import logging
from abc import ABC
from datetime import timedelta
from random import randint, shuffle
from typing import List

from dateutil.relativedelta import relativedelta  # type: ignore
from skye_comlib.utils.formatter import Formatter

from src.connectors.google_calendar import GoogleCalAPI
from src.connectors.trakt import TraktAPI
from src.data.data import Calendars, Data
from src.models.calendar import Calendar, Owner
from src.models.event import Event
from src.models.event_datetime import EventDateTime
from src.models.location.geo_location import GeoLocation
from src.models.trakt.history_item import HistoryItemEpisode, HistoryItemMovie
from src.models.watch import EpisodeWatch, MovieWatch, TempEpisodeWatch, TempMovieWatch, Watch
from src.scripts.script import Script


class MediaScript(Script, ABC):
    calendar = Calendars.lazing

    @classmethod
    def process_watches(
        cls,
        watches: List[Watch],
        calendar: Calendar,
        owner: Owner,
        location: GeoLocation,
    ) -> None:
        logging.info(Formatter.sub_title("Updating history"), extra={"markup": True})

        logging.info("Removing old watches from history")
        cls.remove_watches_from_history(watches)

        logging.info("Adding watches to history")
        TraktAPI.add_episodes_to_history(watches)

        logging.info("Adding watch events to Google Calendar")

        for watch in watches:
            logging.info(f"- {watch.__str__()} {watch.get_start()} - {watch.end}")
            cls.create_watch_event(calendar, owner, watch, location)

    @classmethod
    def remove_watches_from_history(cls, watches: List[Watch]) -> None:
        add_again: List[Watch] = []
        for watch in watches:
            if isinstance(watch, EpisodeWatch):
                results = TraktAPI.get_history_for_episode(watch.episode_id)
                for result in results:
                    old_watch = TempEpisodeWatch.from_result(result)
                    if abs(old_watch.watched_at - watch.end).days > 5:
                        runtime = cls.get_episode_runtime(watch.trakt_id, watch.season_no, watch.episode_no)
                        add_again.append(EpisodeWatch(old_watch, runtime))
            elif isinstance(watch, MovieWatch):
                results = TraktAPI.get_history_for_movie(watch.trakt_id)
                for result in results:
                    old_watch = TempMovieWatch.from_result(result)
                    if abs(old_watch.watched_at - watch.end).days > 5:
                        runtime = cls.get_movie_runtime(watch.trakt_id)
                        add_again.append(MovieWatch(old_watch, runtime))
            else:
                raise Exception("Unknown watch type")

        TraktAPI.remove_episodes_from_history(watches)
        TraktAPI.add_episodes_to_history(add_again)

    @classmethod
    def get_watches_from_episode_history(cls, history: List[HistoryItemEpisode]) -> List[EpisodeWatch]:
        watches = []
        for result in history:
            temp_watch = TempEpisodeWatch.from_result(result)
            runtime = cls.get_episode_runtime(temp_watch.show_id, temp_watch.season_no, temp_watch.episode_no)
            watch = EpisodeWatch(temp_watch, runtime)
            watches.append(watch)
        return watches

    @classmethod
    def get_watches_from_movie_history(cls, history: List[HistoryItemMovie]) -> List[MovieWatch]:
        watches = []
        for result in history:
            temp_watch = TempMovieWatch.from_result(result)
            runtime = cls.get_movie_runtime(temp_watch.movie_id)
            watch = MovieWatch(temp_watch, runtime)
            watches.append(watch)
        return watches

    @classmethod
    def get_episode_runtime(cls, show_id: int, season_no: int, episode_no: int) -> int:
        return cls.get_episode_details(show_id, season_no, episode_no)["runtime"]

    @classmethod
    def get_episode_details(cls, show_id: int, season_no: int, episode_no: int) -> dict:
        # TODO there's an issue if the season is already in the cache but the data has been updated
        try:
            return Data.runtime_cache.get_episode(show_id, season_no, episode_no)

        except KeyError:
            results = TraktAPI.get_season_details(show_id, season_no)

            for result in results:
                cache_entry = {"runtime": result.runtime, "trakt_id": result.ids.trakt, "title": result.title}
                Data.runtime_cache.add_episode(show_id, season_no, result.number, cache_entry)

            return Data.runtime_cache.get_episode(show_id, season_no, episode_no)

    @classmethod
    def get_movie_runtime(cls, movie_id: int) -> int:
        try:
            return Data.runtime_cache.get_movie(movie_id)

        except KeyError:
            result = TraktAPI.get_movie(movie_id)
            Data.runtime_cache.add_movie(movie_id, result.runtime)
            return result.runtime

    @classmethod
    def spread_watches(cls, watches: List[Watch], duration: timedelta) -> List[Watch]:
        total_runtime = sum([x.runtime for x in watches])
        total_breaks = duration.seconds - (total_runtime * 60)

        breaks = [0]
        for _ in range(0, len(watches) - 2):
            breaks.append(randint(0, total_breaks - sum(breaks)))  # noqa: S311
        breaks.pop(0)
        breaks.append(total_breaks - sum(breaks))
        shuffle(breaks)

        for index, watch in enumerate(watches[1:]):
            extra_break = sum(breaks[: index + 1])
            watch.end = watch.end + relativedelta(seconds=extra_break)

        return watches

    @staticmethod
    def create_watch_event(calendar: Calendar, owner: Owner, watch: Watch, location: GeoLocation) -> None:
        event = Event(
            summary=watch.title,
            location=location.address.__str__(),
            description=Formatter.serialise_details(watch.details),
            start=EventDateTime(date_time=watch.get_start(), time_zone=location.time_zone),
            end=EventDateTime(date_time=watch.end, time_zone=location.time_zone),
        )

        GoogleCalAPI.create_event(calendar.get_cal_id(owner), event)
