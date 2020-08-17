import sys

from src.scripts.activity.parse_timing_export import ParseTimingExportScript
from src.scripts.activity.update_calendar import UpdateCalendar
from src.scripts.location.add_location import AddLocation
from src.scripts.location.update_event_times import UpdateEventTimes
from src.scripts.media.add_episode_to_history import AddEpisodesToHistory
from src.scripts.media.add_movie_to_history import AddMovieToHistory
from src.scripts.media.update_period import UpdatePeriod
from src.scripts.media.update_today import UpdateToday
from src.scripts.media.update_yesterday import UpdateYesterday
from src.scripts.work.add_days import AddDays
from src.scripts.work.update_project import UpdateProject
from src.utils.formatter import Formatter
from src.utils.input import Input
from src.utils.logger import Logger

SCRIPTS = {
    'Activity': {
        'Parse timing export': ParseTimingExportScript,
        'Update calendar': UpdateCalendar,
    },
    'Media': {
        'Update Trakt today': UpdateToday,
        'Update Trakt yesterday': UpdateYesterday,
        'Update Trakt period': UpdatePeriod,
        'Add episodes to history': AddEpisodesToHistory,
        'Add movie to history': AddMovieToHistory
    },
    'Locations': {
        'Update event times': UpdateEventTimes,
        'Add new location': AddLocation
    },
    'Work': {
        'Add work days': AddDays,
        'Update work project': UpdateProject,
    }
}

if __name__ == '__main__':
    Logger.title('Selecting script')

    categories = list(SCRIPTS.keys())
    options = '\n'.join(f'{str(index + 1).rjust(4)}) {x}' for index, x in enumerate(categories))
    if len(sys.argv) > 1:
        category_no = int(sys.argv[1]) - 1
    else:
        Logger.empty_line()
        category_no = Input.get_int_input(f'Which category do you want to run?\n{options}\n\nCategory no. ') - 1

    assert category_no in range(0, len(SCRIPTS))
    category = categories[category_no]
    Logger.log(f'Selected {Formatter.make_bold(category)}')

    scripts = list(SCRIPTS[category].keys())
    options = '\n'.join(f'{str(index + 1).rjust(4)}) {x}' for index, x in enumerate(scripts))
    if len(sys.argv) > 2:
        script_no = int(sys.argv[2]) - 1
    else:
        Logger.empty_line()
        script_no = Input.get_int_input(f'Which script do you want to run?\n{options}\n\nScript no. ') - 1

    assert script_no in range(0, len(scripts))
    script_name = scripts[script_no]
    Logger.log(f'Selected {Formatter.make_bold(script_name)}')

    Logger.title('Running script')
    script = SCRIPTS[category][script_name]()
    script.run()

    Logger.title('Done')
