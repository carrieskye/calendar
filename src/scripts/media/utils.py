import csv
import json
from datetime import timedelta
from random import randint, shuffle
from typing import List

from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalAPI
from src.connectors.trakt import TraktAPI
from src.models.calendar import Owner, Calendar
from src.models.event import Event
from src.models.event_datetime import EventDateTime
from src.models.geo_location import GeoLocation
from src.models.watch import Watch, EpisodeWatch, MovieWatch, TempEpisodeWatch, TempMovieWatch
from src.utils.file import File
from src.utils.output import Output


class MediaUtils:
    runtime_cache = File.read_json('data/trakt/cache/runtime.json')

    @classmethod
    def process_watches(cls, watches: List[Watch], calendar: Calendar, owner: Owner, location: GeoLocation):
        for watch in watches:
            cls.remove_watch_from_history(watch)
            TraktAPI.add_episodes_to_history([watch])
            MediaUtils.create_watch_event(calendar, owner, watch, location)

    @classmethod
    def remove_watch_from_history(cls, watch: Watch):
        add_again = []
        if isinstance(watch, EpisodeWatch):
            watches = TraktAPI.get_history_for_episode(watch.episode_id)
            for result in watches:
                old_watch = TempEpisodeWatch.from_result(result)
                if abs(old_watch.watched_at - watch.end).days > 5:
                    runtime = cls.get_episode_runtime(watch.trakt_id, watch.season_no, watch.episode_no)
                    add_again.append(EpisodeWatch(old_watch, runtime))
        TraktAPI.remove_episodes_from_history([watch])
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
    def group_watches(cls, watches: List[Watch], gap: int) -> List[List[Watch]]:
        groups = []
        for index, watch in enumerate(watches):
            if index == 0:
                groups.append([watch])
            else:
                within_gap = watches[index - 1].end + relativedelta(minutes=gap) > watch.get_start()
                same_id = watches[index - 1].trakt_id == watch.trakt_id
                if within_gap and same_id:
                    watch.end = watches[index - 1].end + relativedelta(minutes=watch.runtime)
                    groups[len(groups) - 1].append(watch)
                else:
                    if within_gap:
                        previous_start = groups[len(groups) - 1][0].get_start()
                        previous_group_total_runtime = sum([item.runtime for item in groups[len(groups) - 1]])
                        previous_runtime = relativedelta(minutes=max(previous_group_total_runtime, 30))
                        watch.end = previous_start + previous_runtime + relativedelta(minutes=watch.runtime)

                    groups.append([watch])
        return groups

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
            description=json.dumps(dict(**{'shared': owner == Owner.shared}, **watch.details)),
            start=EventDateTime(watch.get_start(), location.time_zone),
            end=EventDateTime(watch.end, location.time_zone)
        )

        GoogleCalAPI.create_event(calendar.get_cal_id(owner), event)

    @staticmethod
    def process_calendar_event(event: Event):
        full_description = event.description.replace('\n', '<br>')
        for line in full_description.split('<br>'):
            description = line.replace('<a href="https://trakt.tv/', '')
            description = description.replace(' target="_blank"', '')
            description = description.replace('</a>', '')
            url, name = description.split('">')
            url = url.split('/')
            if url[0] == 'shows':
                show_name = url[1]
                season = url[3]
                episode = url[5]
                print(event.summary, show_name, season, episode, name)
            elif url[0] == 'movies':
                print(event.summary, name)
            print()

    @classmethod
    def export_history(cls, history: List[dict]):
        watches = cls.get_watches_from_history(history)
        movies = []
        episodes = []

        for watch in watches:
            if isinstance(watch, EpisodeWatch):
                episodes.append(watch)
            if isinstance(watch, MovieWatch):
                movies.append(watch)

        cls.export_movies(movies)
        cls.export_episodes(episodes)

    @staticmethod
    def export_movies(movies: List[MovieWatch]):
        Output.make_title('Exporting movies')

        movies = sorted(movies, key=lambda x: x.end)
        with open('data/trakt/exports/movies.csv', 'w') as file:
            field_names = ['title', 'year', 'start', 'end']
            movie_writer = csv.DictWriter(file, field_names)

            for movie in movies:
                print(movie.movie_title)
                movie_writer.writerow(movie.get_export_dict())

    @staticmethod
    def export_episodes(episodes: List[EpisodeWatch]):
        Output.make_title('Exporting episodes')

        episodes = sorted(episodes, key=lambda x: (x.slug, x.season_no, x.episode_no))
        shows = {}
        for episode in episodes:
            slug = episode.slug.replace('-', '_')
            if slug not in shows:
                shows[slug] = []
            shows[slug].append(episode)

        for show, episodes in shows.items():
            print(show)
            with open(f'data/trakt/exports/shows/{show}.csv', 'w') as file:
                field_names = ['season', 'episode', 'title', 'start', 'end']
                show_writer = csv.DictWriter(file, field_names)

                for episode in episodes:
                    show_writer.writerow(episode.get_export_dict())
