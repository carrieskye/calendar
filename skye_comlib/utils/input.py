import logging
from datetime import date, datetime, time

from dateutil.parser import parse

from skye_comlib.utils.formatter import Formatter
from skye_comlib.utils.logger import Logger


def _strtobool(val: str) -> int:
    """Same truth set as distutils.util.strtobool (removed in Python 3.12). Returns 0 or 1."""
    v = val.lower()
    if v in ("y", "yes", "t", "true", "on", "1"):
        return 1
    if v in ("n", "no", "f", "false", "off", "0"):
        return 0
    raise ValueError(f"invalid truth value {val!r}")


Logger.configure()


class Input:
    @classmethod
    def get_string_input(cls, name: str, input_type: str = "", default: str = "") -> str:
        prompt = cls.format_input_prompt(name, input_type, default)
        lines = prompt.split("\n")
        for line in lines[:-1]:
            logging.info(line)

        value = input(Formatter.bold(lines[-1]))
        return value if value else default

    @classmethod
    def format_input_prompt(cls, name: str, input_type: str, default: str) -> str:
        prompt = Formatter.bold(Logger.get_prefix() + name)

        if input_type or default:
            prompt += Formatter.bold(" (")

            if input_type:
                prompt += Formatter.bold(input_type)

            if default:
                prompt += f" {default}?" if input_type else f"{default}?"

            prompt += Formatter.bold(")")

        prompt += " "
        return prompt

    @staticmethod
    def get_bool_input(name: str, input_type: str = "y/n", default: str = "n") -> int:
        value = Input.get_string_input(name, input_type, default)
        return _strtobool(value) if value else _strtobool(default)

    @classmethod
    def get_int_input(cls, name: str, input_type: str = "", default: int = 1) -> int:
        value = cls.get_string_input(name, input_type, str(default))
        return int(value) if value else default

    @classmethod
    def get_date_input(
        cls,
        name: str,
        input_type: str = "YYYY-mm-dd",
        default: date = None,
        min_date: date = None,
        max_date: date = None,
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
        default: time = None,
        min_time: time = None,
        max_time: time = None,
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
        default: datetime = None,
        min_date_time: datetime = None,
        max_date_time: datetime = None,
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
