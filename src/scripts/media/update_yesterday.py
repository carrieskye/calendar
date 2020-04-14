from datetime import datetime

from dateutil.relativedelta import relativedelta

from src.scripts.media.update_period import UpdatePeriod


class UpdateYesterday(UpdatePeriod):

    def __init__(self):
        yesterday = datetime(datetime.now().year, datetime.now().month, datetime.now().day) - relativedelta(days=1)
        super().__init__(start=yesterday, days=1)
