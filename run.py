import sys

from scripts.media import UpdatePeriod, UpdateToday, UpdateYesterday, AddToHistory
from scripts.takeout import SplitByDay, SplitByDayFormatted
from scripts.work import AddDays, UpdateProject, CopyToLarry

if __name__ == '__main__':
    requests = {
        'add_work_days': AddDays,
        'update_work_project': UpdateProject,
        'copy_to_larry': CopyToLarry,
        'update_trakt_today': UpdateToday,
        'update_trakt_yesterday': UpdateYesterday,
        'update_trakt_period': UpdatePeriod,
        'add_to_history': AddToHistory,
        'split_takeout': SplitByDay,
        'split_takeout_formatted': SplitByDayFormatted
    }

    script = requests[sys.argv[1]]()
    script.run()
