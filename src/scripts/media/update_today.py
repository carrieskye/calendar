from datetime import datetime

from src.scripts.media.update_period import UpdatePeriod


class UpdateToday(UpdatePeriod):

    def __init__(self):
        today = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
        super().__init__(start=today, days=1)
