from datetime import datetime

from dateutil.relativedelta import relativedelta

from src.connectors.trakt import TraktAPI
from src.models.watch import EpisodeWatch
from src.scripts.media.utils import MediaUtils
from src.scripts.script import Media
from src.utils.input import Input
from src.utils.logger import Logger


class UpdatePeriod(Media):

    def __init__(self, start: datetime = None, days: int = None):
        super().__init__()

        if not start:
            start = Input.get_date_input('Start')
        if not days:
            days = Input.get_int_input('Days', input_type='#days')

        self.start = start + relativedelta(hours=4)
        self.end = self.start + relativedelta(days=int(days))
        self.owner = self.get_owner()
        self.location = self.get_location()

    def run(self):
        Logger.title('Processing')

        history = sorted(TraktAPI.get_history(self.start, self.end), key=lambda x: x.get('watched_at'))
        watches = MediaUtils.get_watches_from_history(history)
        for x in watches:
            Logger.log(x.title + ' ' + x.details['episode'] if isinstance(x, EpisodeWatch) else '')
        MediaUtils.process_watches(watches, self.calendar, self.owner, self.location)
