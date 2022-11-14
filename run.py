import logging
import sys

from skye_comlib.utils.formatter import Formatter
from skye_comlib.utils.input import Input
from skye_comlib.utils.logger import Logger

from src.scripts.activity.larry_default_working_day import LarryDefaultWorkingDayScript
from src.scripts.activity.parse_hayley_export import ParseHayleyExportScript
from src.scripts.activity.parse_timing_export import ParseTimingExportScript
from src.scripts.activity.update_calendar import UpdateCalendar
from src.scripts.location.add_location import AddLocation
from src.scripts.location.print_locations import PrintLocations
from src.scripts.location.update_event_times import UpdateEventTimes
from src.scripts.media.add_episode_to_history import AddEpisodesToHistory
from src.scripts.media.add_movie_to_history import AddMovieToHistory
from src.scripts.media.add_to_calendar import AddToCalendar

Logger.configure()

SCRIPTS = {
    "Activity": {
        "Parse timing export": ParseTimingExportScript,
        "Update calendar": UpdateCalendar,
        "Parse Hayley export": ParseHayleyExportScript,
        "Larry default working day": LarryDefaultWorkingDayScript,
    },
    "Media": {
        "Add Trakt watches to calendar": AddToCalendar,
        "Add episodes to history": AddEpisodesToHistory,
        "Add movie to history": AddMovieToHistory,
    },
    "Locations": {
        "Update event times": UpdateEventTimes,
        "Add new location": AddLocation,
        "Print locations": PrintLocations,
    },
}

if __name__ == "__main__":
    logging.info(Formatter.title("Selecting script"))

    categories = list(SCRIPTS.keys())
    options = "\n".join(f"{str(index + 1).rjust(4)}) {x}" for index, x in enumerate(categories))
    if len(sys.argv) > 1:
        category_no = int(sys.argv[1]) - 1
    else:
        category_no = Input.get_int_input(f"Which category do you want to run?\n{options}\n\nCategory no. ")
        category_no -= 1

    assert category_no in range(0, len(SCRIPTS))
    category = categories[category_no]
    logging.info(f"Selected [bold]{category}", extra={"markup": True})

    scripts = list(SCRIPTS[category].keys())
    options = "\n".join(f"{str(index + 1).rjust(4)}) {x}" for index, x in enumerate(scripts))
    if len(sys.argv) > 2:
        script_no = int(sys.argv[2]) - 1
    else:
        script_no = Input.get_int_input(f"Which script do you want to run?\n{options}\n\nScript no. ")
        script_no -= 1

    assert script_no in range(0, len(scripts))
    script_name = scripts[script_no]
    logging.info(f"Selected [bold]{script_name}", extra={"markup": True})

    logging.info(Formatter.title("Running script"))
    script = SCRIPTS[category][script_name]()
    script.run()
