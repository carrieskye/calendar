from datetime import timedelta
from typing import List

from src.connectors.google_calendar import GoogleCalendarAPI
from src.connectors.trakt import TraktAPI
from src.models.watch import EpisodeWatch, MovieWatch, Watch
from src.models.event import Event
from src.models.event_datetime import EventDateTime
from src.utils import Utils


class Calendar:

    def __init__(self):
        self.google_calendar = GoogleCalendarAPI()
        self.calendars = Utils.read_json('exports/calendars.json')
        self.trakt = TraktAPI()

    def export_calendar_dict(self):
        calendar_list = self.google_calendar.get_calendars()
        calendar_list = {Utils.normalise(calendar.get('summary')): calendar.get('id') for calendar in calendar_list}
        Utils.write_json(calendar_list, 'exports/calendars.json')

    def update_trakt_history(self, start, end, gap=30):
        history = sorted(self.trakt.get_history(start, end), key=lambda x: x.get('watched_at'))
        watches = [EpisodeWatch(result, self.get_details(result)) if result.get('type') == 'episode'
                   else MovieWatch(result, self.get_details(result)) for result in history]
        groups = self.group_watches(watches, gap)

        for group in groups:
            self.trakt.remove_episodes_from_history(group)
            self.trakt.add_episodes_to_history(group)
            group_event = self.create_watch_event(group)
            self.google_calendar.create_event(self.calendars['tv_shared'], group_event)

    def get_details(self, result):
        if result.get('type') == 'episode':
            show_id = result.get('show').get('ids').get('trakt')
            season_no = result.get('episode').get('season')
            episode_no = result.get('episode').get('number')
            return self.trakt.get_episode(show_id, season_no, episode_no)
        else:
            movie_id = result.get('movie').get('ids').get('trakt')
            return self.trakt.get_movie(movie_id)

    @classmethod
    def group_watches(cls, watches: List[Watch], gap):
        groups = []
        for index, watch in enumerate(watches):
            if index == 0:
                watch.end = watch.end - timedelta(seconds=watch.end.second)
                groups.append([watch])
            else:
                within_gap = watches[index - 1].end + timedelta(seconds=gap * 60) > watch.get_start()
                same_id = watches[index - 1].trakt_id == watch.trakt_id
                if within_gap and same_id:
                    watch.end = watches[index - 1].end + timedelta(seconds=watch.runtime * 60)
                    groups[len(groups) - 1].append(watch)
                else:
                    if within_gap:
                        watch.end = watches[index - 1].end + timedelta(seconds=(watch.runtime + 15) * 60)

                    groups.append([watch])
        return groups

    @classmethod
    def create_watch_event(cls, watches: List[Watch]):
        return Event(
            summary=watches[0].title,
            location='25 Bromsgrove St, Cardiff CF11 7EZ, UK',
            description='\n'.join([watch.get_title() for watch in watches if isinstance(watch, EpisodeWatch)]),
            start=EventDateTime(watches[0].get_start() + timedelta(seconds=3600), 'Europe/London'),
            end=EventDateTime(watches[-1].end + timedelta(seconds=3600), 'Europe/London')
        )
