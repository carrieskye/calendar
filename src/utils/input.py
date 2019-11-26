from datetime import datetime, date, time
from distutils.util import strtobool
from typing import List

from dateutil.parser import parse

from src.utils.output import Output


class Input:

    @staticmethod
    def get_inputs(fields: List):
        results = []
        for field in fields:
            field_type, name, default = (field + (None,))[:3]
            results.append(Input.get_input(field_type, name, default))
        return results

    @staticmethod
    def get_input(field_type, name: str, default=None):
        if field_type == str:
            return Input.get_string_input(name, default) if default else Input.get_string_input(name)
        elif field_type == int:
            return Input.get_int_input(name, default) if default else Input.get_int_input(name)
        elif field_type == date:
            return Input.get_date_input(name, default) if default else Input.get_date_input(name)
        elif field_type == datetime:
            return Input.get_date_time_input(name, default) if default else Input.get_date_time_input(name)
        else:
            raise Exception(f'Unknown input type: {type}')

    @staticmethod
    def get_string_input(name: str, default: str = ''):
        bold = "\033[1m"
        reset = "\033[0;0m"
        prompt = f'{name}: ' if not default else f'{name} ({default}): '
        value = input(bold + prompt + reset)
        return value if value else default

    @staticmethod
    def get_bool_input(name: str, default: str = 'y/n'):
        value = Input.get_string_input(name, default)
        return strtobool(value) if value != 'y/n' else False

    @staticmethod
    def get_int_input(name: str, default: int = 1):
        value = Input.get_string_input(name, str(default))
        return int(value) if value else default

    @staticmethod
    def get_date_input(name: str, default: date = datetime.now().date(), min_date: date = None, max_date: date = None):
        value = Input.get_string_input(name, default.strftime('%Y-%m-%d'))
        parsed = parse(value).date() if value else default

        if min_date and parsed < min_date:
            Output.make_bold(f'Minimum date is {min_date}')
            return Input.get_date_input(name, default, min_date, max_date)

        if max_date and parsed > max_date:
            Output.make_bold(f'Maximum date is {max_date}')
            return Input.get_date_input(name, default, min_date, max_date)

        return parsed

    @staticmethod
    def get_time_input(name: str, default: time = datetime.now().time(), min_time: time = None, max_time: time = None):
        value = Input.get_string_input(name, default.strftime('%H:%M'))
        parsed = parse(value).time() if value else default

        if min_time and parsed < min_time:
            Output.make_bold(f'Minimum time is {min_time}')
            return Input.get_time_input(name, default, min_time, max_time)

        if max_time and parsed > max_time:
            Output.make_bold(f'Maximum time is {max_time}')
            return Input.get_time_input(name, default, min_time, max_time)

        return parsed

    @staticmethod
    def get_date_time_input(name: str, default: datetime = datetime.now(), min_date_time: datetime = None,
                            max_date_time: datetime = None):
        date_part = Input.get_date_input(name + 'date', default.date())
        time_part = Input.get_time_input(name + 'time', default.time())
        parsed = datetime.combine(date_part, time_part)

        if min_date_time and parsed < min_date_time:
            Output.make_bold(f'Minimum datetime is {min_date_time}')
            return Input.get_date_time_input(name, default, min_date_time, max_date_time)

        if max_date_time and parsed > max_date_time:
            Output.make_bold(f'Maximum datetime is {max_date_time}')
            return Input.get_date_time_input(name, default, min_date_time, max_date_time)

        return parsed
