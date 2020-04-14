from datetime import datetime, date, time
from distutils.util import strtobool

from dateutil.parser import parse

from src.utils.output import Output


class Input:

    @staticmethod
    def get_string_input(name: str, input_type: str = 'str', default: str = ''):
        bold = "\033[1m"
        reset = "\033[0;0m"
        prompt = bold + f'{name} ({input_type}' + reset
        prompt += f' {default}?' + bold + '): ' + reset if default else bold + '): ' + reset
        value = input(prompt)
        return value if value else default

    @staticmethod
    def get_bool_input(name: str, input_type: str = 'y/n', default: str = 'n'):
        value = Input.get_string_input(name, input_type, default)
        return strtobool(value) if value else strtobool(default)

    @staticmethod
    def get_int_input(name: str, input_type: str, default: int = 1):
        value = Input.get_string_input(name, input_type, str(default))
        return int(value) if value else default

    @staticmethod
    def get_date_input(name: str, input_type: str = 'YYYY-mm-dd', default: date = datetime.now().date(),
                       min_date: date = None, max_date: date = None) -> date:
        value = Input.get_string_input(name, input_type, default.strftime('%Y-%m-%d'))
        parsed = parse(value).date() if value else default

        if min_date and parsed < min_date:
            Output.make_bold(f'Minimum date is {min_date}')
            return Input.get_date_input(name, input_type, default, min_date, max_date)

        if max_date and parsed > max_date:
            Output.make_bold(f'Maximum date is {max_date}')
            return Input.get_date_input(name, input_type, default, min_date, max_date)

        return parsed

    @staticmethod
    def get_time_input(name: str, input_type: str = 'HH:MM:SS', default: time = datetime.now().time(),
                       min_time: time = None, max_time: time = None):
        value = Input.get_string_input(name, input_type, default.strftime('%H:%M:%S'))
        parsed = parse(value).time() if value else default

        if min_time and parsed < min_time:
            Output.make_bold(f'Minimum time is {min_time}')
            return Input.get_time_input(name, input_type, default, min_time, max_time)

        if max_time and parsed > max_time:
            Output.make_bold(f'Maximum time is {max_time}')
            return Input.get_time_input(name, input_type, default, min_time, max_time)

        return parsed

    @staticmethod
    def get_date_time_input(name: str, input_type: str = 'YYYY-mm-dd HH:MM', default: datetime = datetime.now(),
                            min_date_time: datetime = None, max_date_time: datetime = None):
        date_part = Input.get_date_input(name + 'date', default=default.date())
        time_part = Input.get_time_input(name + 'time', default=default.time())
        parsed = datetime.combine(date_part, time_part)

        if min_date_time and parsed < min_date_time:
            Output.make_bold(f'Minimum datetime is {min_date_time}')
            return Input.get_date_time_input(name, input_type, default, min_date_time, max_date_time)

        if max_date_time and parsed > max_date_time:
            Output.make_bold(f'Maximum datetime is {max_date_time}')
            return Input.get_date_time_input(name, input_type, default, min_date_time, max_date_time)

        return parsed
