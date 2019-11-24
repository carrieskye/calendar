from typing import List

from dateutil.relativedelta import relativedelta

from src.connectors.google_calendar import GoogleCalendarAPI
from src.connectors.trakt import TraktAPI
from src.models.event import Event
from src.models.event_datetime import EventDateTime
from src.models.watch import Watch, EpisodeWatch, MovieWatch


class MediaUtils:

    def __init__(self):
        self.google_cal = GoogleCalendarAPI()
        self.trakt_api = TraktAPI()

        self.locations = {
            'bromsgrove': {'full': '25 Bromsgrove St, Cardiff CF11 7EZ, UK', 'name': 'Europe/London'},
            'newport': {'full': '118 Newport Rd, Cardiff CF24 1DH, UK', 'name': 'Europe/London'},
            'kleinbeeklei': {'full': 'Kleinbeeklei 30, 2820 Bonheiden, Belgium', 'name': 'Europe/Brussels'},
            'kruisstraat': {'full': 'Kruisstraat 36, 3850 Nieuwerkerken, Belgium', 'name': 'Europe/Brussels'}
        }

    def process_watches(self, watches: List[Watch], calendar_id: str, location: str, gap: int):
        groups = MediaUtils.group_watches(watches, gap)

        for group in groups:
            self.trakt_api.remove_episodes_from_history(group)
            self.trakt_api.add_episodes_to_history(group)
            group_event = MediaUtils.create_watch_event(group, self.locations[location])
            self.google_cal.create_event(calendar_id, group_event)

    def get_watches_from_history(self, history: List[dict]):
        watches = []
        for result in history:
            if result.get('type') == 'episode':
                watch = EpisodeWatch(watched_at=result.get('watched_at'),
                                     show=result.get('show'),
                                     episode=self.get_details(result))
            else:
                watch = MovieWatch(watched_at=result.get('watched_at'),
                                   summary=result.get('movie'),
                                   details=self.get_details(result))
            watches.append(watch)
        return watches

    def get_details(self, result: dict):
        if result.get('type') == 'episode':
            show_id = result.get('show').get('ids').get('trakt')
            season_no = result.get('episode').get('season')
            episode_no = result.get('episode').get('number')
            return self.trakt_api.get_episode(show_id, season_no, episode_no)
        else:
            movie_id = result.get('movie').get('ids').get('trakt')
            return self.trakt_api.get_movie(movie_id)

    @staticmethod
    def group_watches(watches: List[Watch], gap: int):
        groups = []
        for index, watch in enumerate(watches):
            if index == 0:
                watch.end = watch.end - relativedelta(seconds=watch.end.second)
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
