from abc import ABC
from datetime import timedelta
from random import randint, shuffle
from typing import List

from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalAPI
from src.connectors.trakt import TraktAPI
from src.data.data import Calendars
from src.models.calendar import Owner, Calendar
from src.models.event import Event
from src.models.event_datetime import EventDateTime
from src.models.geo_location import GeoLocation
from src.models.watch import Watch, EpisodeWatch, MovieWatch, TempEpisodeWatch, TempMovieWatch
from src.scripts.script import Script
from src.utils.file import File
from src.utils.formatter import Formatter
from src.utils.logger import Logger


class MediaScript(Script, ABC):
    calendar = Calendars.leisure
    runtime_cache = File.read_json('data/trakt/cache/runtime.json')

    @classmethod
    def process_watches(cls, watches: List[Watch], calendar: Calendar, owner: Owner, location: GeoLocation):
        Logger.sub_title('Updating history')

        Logger.log('Removing old watches from history')
        cls.remove_watches_from_history(watches)

        Logger.log('Adding watches to history')
        TraktAPI.add_episodes_to_history(watches)

        Logger.log('Adding watch events to Google Calendar')

        for watch in watches:
            Logger.log(f'- {watch.__str__()} {watch.get_start()} - {watch.end}', indent=1)
            cls.create_watch_event(calendar, owner, watch, location)

    @classmethod
    def remove_watches_from_history(cls, watches: List[Watch]):
        add_again = []
        for watch in watches:
            if isinstance(watch, EpisodeWatch):
                results = TraktAPI.get_history_for_episode(watch.episode_id)
                for result in results:
                    old_watch = TempEpisodeWatch.from_result(result)
                    if abs(old_watch.watched_at - watch.end).days > 5:
                        runtime = cls.get_episode_runtime(watch.trakt_id, watch.season_no, watch.episode_no)
                        add_again.append(EpisodeWatch(old_watch, runtime))
        TraktAPI.remove_episodes_from_history(watches)
        TraktAPI.add_episodes_to_history(add_again)

    @classmethod
    def get_watches_from_history(cls, history: List[dict]) -> List[Watch]:
        watches = []
        for result in history:
            if result.get('type') == 'episode':
                temp_watch = TempEpisodeWatch.from_result(result)
                runtime = cls.get_episode_runtime(temp_watch.show_id, temp_watch.season_no, temp_watch.episode_no)
                watch = EpisodeWatch(temp_watch, runtime)
            else:
                temp_watch = TempMovieWatch.from_result(result)
                runtime = cls.get_movie_runtime(temp_watch.movie_id)
                watch = MovieWatch(temp_watch, runtime)
            watches.append(watch)
        return watches

    @classmethod
    def get_episode_runtime(cls, show_id: str, season_no: str, episode_no: int) -> int:
        return cls.get_episode_details(show_id, season_no, str(episode_no))['runtime']

    @classmethod
    def get_episode_details(cls, show_id: str, season_no: str, episode_no: str):
        # TODO there's an issue if the season is already in the cache but the data has been updated
        try:
            return cls.runtime_cache['shows'][str(show_id)][str(season_no)][str(episode_no)]

        except KeyError:
            results = TraktAPI.get_season_details(show_id, season_no)

            if show_id not in cls.runtime_cache['shows']:
                cls.runtime_cache['shows'][show_id] = {}

            cache_entry = {str(result.get('number')): {
                'runtime': result.get('runtime'),
                'trakt_id': result.get('ids').get('trakt'),
                'title': result.get('title')
            } for result in results}
            cls.runtime_cache['shows'][show_id][season_no] = cache_entry
            File.write_json(cls.runtime_cache, 'data/trakt/cache/runtime.json')

            return cache_entry[str(episode_no)]

    @classmethod
    def get_movie_runtime(cls, movie_id: str):
        try:
            return cls.runtime_cache['movies'][movie_id]

        except KeyError:
            result = TraktAPI.get_movie(movie_id)

            cls.runtime_cache['movies'][movie_id] = result.get('runtime')
            File.write_json(cls.runtime_cache, 'data/trakt/cache/runtime.json')

            return result.get('runtime')

    @classmethod
    def spread_watches(cls, watches: List[Watch], duration: timedelta) -> List[Watch]:
        total_runtime = sum([x.runtime for x in watches])
        total_breaks = duration.seconds - (total_runtime * 60)

        breaks = [0]
        for _ in range(0, len(watches) - 2):
            breaks.append(randint(0, total_breaks - sum(breaks)))
        breaks.pop(0)
        breaks.append(total_breaks - sum(breaks))
        shuffle(breaks)

        for index, watch in enumerate(watches[1:]):
            extra_break = sum(breaks[:index + 1])
            watch.end = watch.end + relativedelta(seconds=extra_break)

        return watches

    @staticmethod
    def create_watch_event(calendar: Calendar, owner: Owner, watch: Watch, location: GeoLocation):
        event = Event(
            summary=watch.title,
            location=location.address.__str__(),
            description=Formatter.serialise_details(watch.details),
            start=EventDateTime(watch.get_start(), location.time_zone),
            end=EventDateTime(watch.end, location.time_zone)
        )

        GoogleCalAPI.create_event(calendar.get_cal_id(owner), event)
