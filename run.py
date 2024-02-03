import argparse
from typing import Dict, List, Type

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
from src.scripts.script import Script

Logger.configure()


def run_multiple(task_dict: dict, tasks_str: str) -> None:
    task_names = list(task_dict.keys())
    if not tasks_str:
        tasks_str = input(
            "Please select tasks:" + "\n".join([f"{idx}) {task}" for idx, task in enumerate(task_names)]) + "\nTasks: ",
        )
    tasks: List[int] = []
    for number in tasks_str.split(","):
        if "-" in number:
            start, end = number.split("-")
            tasks += range(int(start), int(end) + 1)
        else:
            tasks.append(int(number))
    for task in tasks:
        _script = task_dict[task_names[task]]()
        _script.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    FUNCTION_MAP: Dict[str, Type[Script]] = {
        "Parse timing export": ParseTimingExportScript,  # 0
        "Update calendar": UpdateCalendar,  # 1
        "Parse Hayley export": ParseHayleyExportScript,  # 2
        "Larry default working day": LarryDefaultWorkingDayScript,  # 3
        "Add Trakt watches to calendar": AddToCalendar,  # 4
        "Add episodes to history": AddEpisodesToHistory,  # 5
        "Add movie to history": AddMovieToHistory,  # 6
        "Update event times": UpdateEventTimes,  # 7
        "Add new location": AddLocation,  # 8
        "Print locations": PrintLocations,  # 9
    }
    parser.add_argument("--task", "--t", choices=FUNCTION_MAP.keys(), required=False)
    parser.add_argument("--numbers", "--n", type=str, required=False)
    args = parser.parse_args()
    try:
        script: Script = FUNCTION_MAP[args.task]()
        script.run()
    except KeyError:
        run_multiple(FUNCTION_MAP, args.numbers)
