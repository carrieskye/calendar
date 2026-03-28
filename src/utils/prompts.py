"""Interactive prompts using Rich (Prompt / IntPrompt / Confirm)."""
import logging
from datetime import date, datetime, time
from typing import Optional

from dateutil.parser import parse
from rich.prompt import Confirm, IntPrompt, Prompt


_INPUT_PREFIX = "                    "


class Input:
    @classmethod
    def get_string_input(cls, name: str, input_type: str = "", default: str = "") -> str:
        label = f"{_INPUT_PREFIX}{name}"
        if input_type or default:
            label += " ("
            if input_type:
                label += input_type
            if default:
                label += f" {default}?" if input_type else f"{default}?"
            label += ")"
        result = Prompt.ask(label, default=default or "", show_default=bool(default))
        return result if result else default

    @classmethod
    def get_int_input(cls, name: str, input_type: str = "", default: int = 1) -> int:
        label = f"{_INPUT_PREFIX}{name}"
        if input_type:
            label += f" ({input_type})"
        return IntPrompt.ask(label, default=default)

    @staticmethod
    def get_bool_input(name: str, input_type: str = "y/n", default: str = "n") -> int:
        default_bool = default.lower() in ("y", "yes", "t", "true", "on", "1")
        label = f"{_INPUT_PREFIX}{name}"
        if input_type:
            label += f" ({input_type})"
        return 1 if Confirm.ask(label, default=default_bool) else 0

    @classmethod
    def get_date_input(
        cls,
        name: str,
        input_type: str = "YYYY-mm-dd",
        default: Optional[date] = None,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
    ) -> date:
        if default is None:
            default = datetime.now().date()
        value = cls.get_string_input(name, input_type, default.strftime("%Y-%m-%d"))
        parsed = parse(value).date() if value else default

        if min_date and parsed < min_date:
            logging.error(f"Minimum date is {min_date}")
            return cls.get_date_input(name, input_type, default, min_date, max_date)

        if max_date and parsed > max_date:
            logging.error(f"Maximum date is {max_date}")
            return cls.get_date_input(name, input_type, default, min_date, max_date)

        return parsed

    @staticmethod
    def get_time_input(
        name: str,
        input_type: str = "HH:MM:SS",
        default: Optional[time] = None,
        min_time: Optional[time] = None,
        max_time: Optional[time] = None,
    ) -> time:
        if default is None:
            default = datetime.now().time()
        value = Input.get_string_input(name, input_type, default.strftime("%H:%M:%S"))
        parsed = parse(value).time() if value else default

        if min_time and parsed < min_time:
            logging.error(f"Minimum time is {min_time}")
            return Input.get_time_input(name, input_type, default, min_time, max_time)

        if max_time and parsed > max_time:
            logging.error(f"Maximum time is {max_time}")
            return Input.get_time_input(name, input_type, default, min_time, max_time)

        return parsed

    @staticmethod
    def get_date_time_input(
        name: str,
        input_type: str = "YYYY-mm-dd HH:MM",
        default: Optional[datetime] = None,
        min_date_time: Optional[datetime] = None,
        max_date_time: Optional[datetime] = None,
    ) -> datetime:
        if default is None:
            default = datetime.now()
        date_part = Input.get_date_input(name + "date", default=default.date())
        time_part = Input.get_time_input(name + "time", default=default.time())
        parsed = datetime.combine(date_part, time_part)

        if min_date_time and parsed < min_date_time:
            logging.error(f"Minimum datetime is {min_date_time}")
            return Input.get_date_time_input(name, input_type, default, min_date_time, max_date_time)

        if max_date_time and parsed > max_date_time:
            logging.error(f"Maximum datetime is {max_date_time}")
            return Input.get_date_time_input(name, input_type, default, min_date_time, max_date_time)

        return parsed
