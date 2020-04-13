from src.connectors.google_calendar import GoogleCalAPI
from src.data.data import Calendars
from src.scripts.locations.add_location import AddLocation
from src.scripts.locations.update_event_times import UpdateEventTimes
from src.scripts.media import UpdatePeriod, UpdateToday, UpdateYesterday, AddToHistory
from src.scripts.takeout import SplitByDay, SplitByDayFormatted
from src.scripts.work.add_days import AddDays
from src.scripts.work.update_hours import UpdateHours
from src.scripts.work.work import UpdateProject, CopyToLarry

SCRIPTS = {
    'Work': {
        'Add work days': AddDays,
        'Update work hours': UpdateHours,
        'Update work project': UpdateProject,
        'Copy work hours to Larry': CopyToLarry
    },
    'Media': {
        'Update Trakt today': UpdateToday,
        'Update Trakt yesterday': UpdateYesterday,
        'Update Trakt period': UpdatePeriod,
        'Add media to history': AddToHistory
    },
    'Takeout': {
        'Split takeout': SplitByDay,
        'Split takeout formatted': SplitByDayFormatted
    },
    'Locations': {
        'Update event times': UpdateEventTimes,
        'Add new location': AddLocation
    }
}

if __name__ == '__main__':
    categories = list(SCRIPTS.keys())
    options = '\n'.join(f'{str(index + 1).rjust(4)}) {x}' for index, x in enumerate(categories))
    category_no = int(input(f'\nWhich category do you want to run?\n{options}\n\nCategory no. ')) - 1

    assert category_no in range(0, len(SCRIPTS))
    category = categories[category_no]
    print(f'Selected "{category}"')

    scripts = list(SCRIPTS[category].keys())
    options = '\n'.join(f'{str(index + 1).rjust(4)}) {x}' for index, x in enumerate(scripts))
    script_no = int(input(f'\nWhich script do you want to run?\n{options}\n\nScript no. ')) - 1

    assert script_no in range(0, len(scripts))
    script_name = scripts[script_no]
    print(f'Selected "{script_name}"')

    script = SCRIPTS[category][script_name]()
    script.run()
