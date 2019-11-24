from datetime import datetime, date, time
from typing import List

from dateutil.parser import parse

from src.utils.output import Output


class Input:

    @staticmethod
    def get_inputs(fields: List, title: str = 'Input'):
        Output.make_title(title)
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
    def get_int_input(name: str, default: int = 1):
        value = Input.get_string_input(name, str(default))
        return int(value) if value else default

    @staticmethod
    def get_date_input(name: str, default: date = datetime.now().date()):
        value = Input.get_string_input(name, default.strftime('%Y-%m-%d'))
        return parse(value).date() if value else default

    @staticmethod
    def get_time_input(name: str, default: time = datetime.now().time()):
        value = Input.get_string_input(name, default.strftime('%H:%M'))
        return parse(value).time() if value else default

    @staticmethod
    def get_date_time_input(name: str, default: datetime = datetime.now()):
        date_part = Input.get_date_input(name + 'date', default.date())
        time_part = Input.get_time_input(name + 'time', default.time())
        return datetime.combine(date_part, time_part)
