import argparse
from typing import Type

from src.scripts import Script
from src.scripts.activity import (
    ParseChildExportScript,
    ParseTimingExportScript,
    PartnerDefaultWorkingDayScript,
    UpdateCalendar,
)
from src.scripts.location import AddLocation, PrintLocations, UpdateEventTimes
from src.scripts.media import AddEpisodesToHistory, AddMovieToHistory, AddToCalendar
from src.utils import configure_logging

configure_logging()


def run_multiple(task_dict: dict, tasks_str: str) -> None:
    task_names = list(task_dict.keys())
    if not tasks_str:
        tasks_str = input(
            "Please select tasks:" + "\n".join([f"{idx}) {task}" for idx, task in enumerate(task_names)]) + "\nTasks: ",
        )
    tasks: list[int] = []
    for number in tasks_str.split(","):
        if "-" in number:
            start, end = number.split("-")
            tasks += range(int(start), int(end) + 1)
        else:
            tasks.append(int(number))
    for task in tasks:
        _script = task_dict[task_names[task]]()
        _script.run()


FUNCTION_MAP: dict[str, Type[Script]] = {
    "Parse timing export": ParseTimingExportScript,  # 0
    "Update calendar": UpdateCalendar,  # 1
    "Parse Child export": ParseChildExportScript,  # 2
    "Partner default working day": PartnerDefaultWorkingDayScript,  # 3
    "Add Trakt watches to calendar": AddToCalendar,  # 4
    "Add episodes to history": AddEpisodesToHistory,  # 5
    "Add movie to history": AddMovieToHistory,  # 6
    "Update event times": UpdateEventTimes,  # 7
    "Add new location": AddLocation,  # 8
    "Print locations": PrintLocations,  # 9
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", "--t", choices=FUNCTION_MAP.keys(), required=False)
    parser.add_argument("--numbers", "--n", type=str, required=False)
    args = parser.parse_args()
    if args.task is not None:
        script: Script = FUNCTION_MAP[args.task]()
        script.run()
    else:
        run_multiple(FUNCTION_MAP, args.numbers or "")


if __name__ == "__main__":
    main()
