import csv
from typing import List

from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalendarAPI
from src.connectors.trakt import TraktAPI
from src.models.event import Event
from src.models.event_datetime import EventDateTime
from src.models.watch import Watch, EpisodeWatch, MovieWatch, TempEpisodeWatch, TempMovieWatch
from src.utils.output import Output
from src.utils.utils import Utils


class MediaUtils:

    def __init__(self):
        self.google_cal = GoogleCalendarAPI()
        self.trakt_api = TraktAPI()
        self.runtime_cache = Utils.read_json('data/trakt/cache/runtime.json')

        self.locations = {
            'bromsgrove': {'full': '25 Bromsgrove St, Cardiff CF11 7EZ, UK', 'name': 'Europe/London'},
            'newport': {'full': '118 Newport Rd, Cardiff CF24 1DH, UK', 'name': 'Europe/London'},
            'kleinbeeklei': {'full': 'Kleinbeeklei 30, 2820 Bonheiden, Belgium', 'name': 'Europe/Brussels'},
            'kruisstraat': {'full': 'Kruisstraat 36, 3850 Nieuwerkerken, Belgium', 'name': 'Europe/Brussels'}
        }

    def process_watches(self, watches: List[Watch], calendar_id: str, location: str, gap: int):
        groups = MediaUtils.group_watches(watches, gap)

        for group in groups:
            self.remove_watches_from_history(group)
            self.trakt_api.add_episodes_to_history(group)
            group_event = MediaUtils.create_watch_event(group, self.locations[location])
            self.google_cal.create_event(calendar_id, group_event)

    def remove_watches_from_history(self, group: List[Watch]):
        add_again = []
        for watch in group:
            if isinstance(watch, EpisodeWatch):
                watches = self.trakt_api.get_history_for_episode(watch.episode_id)
                for result in watches:
                    old_watch = TempEpisodeWatch.from_result(result)
                    if abs(old_watch.watched_at - watch.end).days > 5:
                        runtime = self.get_episode_runtime(watch.trakt_id, watch.season_no, watch.episode_no)
                        add_again.append(EpisodeWatch(old_watch, runtime))
        self.trakt_api.remove_episodes_from_history(group)
        self.trakt_api.add_episodes_to_history(add_again)

    def get_watches_from_history(self, history: List[dict]):
        watches = []
        for result in history:
            if result.get('type') == 'episode':
                temp_watch = TempEpisodeWatch.from_result(result)
                runtime = self.get_episode_runtime(temp_watch.show_id, temp_watch.season_no, temp_watch.episode_no)
                watch = EpisodeWatch(temp_watch, runtime)
            else:
                temp_watch = TempMovieWatch.from_result(result)
                runtime = self.get_movie_runtime(temp_watch.movie_id)
                watch = MovieWatch(temp_watch, runtime)
            watches.append(watch)
        return watches

    def get_episode_runtime(self, show_id: str, season_no: str, episode_no: int):
        return self.get_episode_details(show_id, season_no, episode_no)['runtime']

    def get_episode_details(self, show_id: str, season_no: str, episode_no: int):
        try:
            return self.runtime_cache['shows'][str(show_id)][str(season_no)][str(episode_no)]

        except KeyError:
            results = self.trakt_api.get_season_details(show_id, season_no)

            if show_id not in self.runtime_cache['shows']:
                self.runtime_cache['shows'][show_id] = {}

            cache_entry = {str(result.get('number')): {
                'runtime': result.get('runtime'),
                'trakt_id': result.get('ids').get('trakt'),
                'title': result.get('title')
            } for result in results}
            self.runtime_cache['shows'][show_id][season_no] = cache_entry
            Utils.write_json(self.runtime_cache, 'data/trakt/cache/runtime.json')

            return cache_entry[str(episode_no)]

    def get_movie_runtime(self, movie_id: str):
        try:
            return self.runtime_cache['movies'][movie_id]

        except KeyError:
            result = self.trakt_api.get_movie(movie_id)

            self.runtime_cache['movies'][movie_id] = result.get('runtime')
            Utils.write_json(self.runtime_cache, 'data/trakt/cache/runtime.json')

            return result.get('runtime')

    @staticmethod
    def group_watches(watches: List[Watch], gap: int):
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

    @staticmethod
    def create_watch_event(watches: List[Watch], location: dict):
        return Event(
            summary=watches[0].title,
            location=location.get('full'),
            description='\n'.join([watch.get_description() for watch in watches]),
            start=EventDateTime(watches[0].get_start(), location.get('name')),
            end=EventDateTime(watches[-1].end, location.get('name'))
        )

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

    def export_history(self, history: List[dict]):
        watches = self.get_watches_from_history(history)
        movies = []
        episodes = []

        for watch in watches:
            if isinstance(watch, EpisodeWatch):
                episodes.append(watch)
            if isinstance(watch, MovieWatch):
                movies.append(watch)

        self.export_movies(movies)
        self.export_episodes(episodes)

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
