import sys

from src.scripts.locations.add_location import AddLocation
from src.scripts.locations.update_event_times import UpdateEventTimes
from src.scripts.media.add_episode_to_history import AddEpisodesToHistory
from src.scripts.media.add_movie_to_history import AddMovieToHistory
from src.scripts.media.update_period import UpdatePeriod
from src.scripts.media.update_today import UpdateToday
from src.scripts.media.update_yesterday import UpdateYesterday
from src.scripts.work.add_days import AddDays
from src.scripts.work.copy_to_larry import CopyToLarry
from src.scripts.work.parse_timing_export import ParseTimingExportScript
from src.scripts.work.update_hours import UpdateHours
from src.scripts.work.update_project import UpdateProject
from src.utils.output import Output

SCRIPTS = {
    'Work': {
        'Add work days': AddDays,
        'Parse timing export': ParseTimingExportScript,
        'Update work hours': UpdateHours,
        'Update work project': UpdateProject,
        'Copy to Larry': CopyToLarry
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
    }
}

if __name__ == '__main__':
    categories = list(SCRIPTS.keys())
    options = '\n'.join(f'{str(index + 1).rjust(4)}) {x}' for index, x in enumerate(categories))
    if len(sys.argv) > 1:
        category_no = int(sys.argv[1]) - 1
    else:
        category_no = int(input(f'\nWhich category do you want to run?\n{options}\n\nCategory no. ')) - 1

    assert category_no in range(0, len(SCRIPTS))
    category = categories[category_no]
    print(f'Selected "{category}"')

    scripts = list(SCRIPTS[category].keys())
    options = '\n'.join(f'{str(index + 1).rjust(4)}) {x}' for index, x in enumerate(scripts))
    if len(sys.argv) > 2:
        script_no = int(sys.argv[2]) - 1
    else:
        script_no = int(input(f'\nWhich script do you want to run?\n{options}\n\nScript no. ')) - 1

    assert script_no in range(0, len(scripts))
    script_name = scripts[script_no]
    print(f'Selected "{script_name}"')

    script = SCRIPTS[category][script_name]()
    script.run()

    Output.make_bold('\nDONE\n')
