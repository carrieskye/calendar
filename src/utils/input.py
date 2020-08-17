from datetime import datetime, date, time
from distutils.util import strtobool
from inspect import getframeinfo, stack, Traceback

from dateutil.parser import parse

from src.utils.formatter import Formatter
from src.utils.logger import Logger


class Input:

    @classmethod
    def get_string_input(cls, name: str, input_type: str = '', default: str = '', caller: Traceback = None):
        if not caller:
            caller = getframeinfo(stack()[1][0])

        prompt = cls.format_input_prompt(name, input_type, default)
        lines = prompt.split('\n')
        for line in lines[:-1]:
            Logger.log(Formatter.make_bold(line), caller=caller)

        value = input(f'{Logger.get_prefix(caller=caller)}    {Formatter.make_bold(lines[-1])}')
        value = value if value else default

        Logger.on_title = False
        Logger.log_file.write(f'{Logger.get_prefix(caller=caller)}    {name}: {value}\n')

        return value

    @classmethod
    def format_input_prompt(cls, name: str, input_type: str, default: str) -> str:
        prompt = Formatter.make_bold(name)

        if input_type or default:
            prompt += Formatter.make_bold(' (')

            if input_type:
                prompt += Formatter.make_bold(input_type)

            if default:
                prompt += f' {default}?' if input_type else f'{default}?'

            prompt += Formatter.make_bold(')')

        prompt += ' '
        return prompt

    @staticmethod
    def get_bool_input(name: str, input_type: str = 'y/n', default: str = 'n'):
        value = Input.get_string_input(name, input_type, default, caller=getframeinfo(stack()[1][0]))
        return strtobool(value) if value else strtobool(default)

    @classmethod
    def get_int_input(cls, name: str, input_type: str = '', default: int = 1):
        value = cls.get_string_input(name, input_type, str(default), caller=getframeinfo(stack()[1][0]))
        return int(value) if value else default

    @classmethod
    def get_date_input(cls, name: str, input_type: str = 'YYYY-mm-dd', default: date = datetime.now().date(),
                       min_date: date = None, max_date: date = None, caller: Traceback = None) -> date:
        caller = caller if caller else getframeinfo(stack()[1][0])
        value = cls.get_string_input(name, input_type, default.strftime('%Y-%m-%d'), caller)
        parsed = parse(value).date() if value else default

        if min_date and parsed < min_date:
            Logger.bold(f'Minimum date is {min_date}')
            return cls.get_date_input(name, input_type, default, min_date, max_date, caller)

        if max_date and parsed > max_date:
            Logger.bold(f'Maximum date is {max_date}')
            return cls.get_date_input(name, input_type, default, min_date, max_date, caller)

        return parsed

    @staticmethod
    def get_time_input(name: str, input_type: str = 'HH:MM:SS', default: time = datetime.now().time(),
                       min_time: time = None, max_time: time = None, caller: Traceback = None):
        caller = caller if caller else getframeinfo(stack()[1][0])
        value = Input.get_string_input(name, input_type, default.strftime('%H:%M:%S'), caller)
        parsed = parse(value).time() if value else default

        if min_time and parsed < min_time:
            Logger.bold(f'Minimum time is {min_time}')
            return Input.get_time_input(name, input_type, default, min_time, max_time, caller)

        if max_time and parsed > max_time:
            Logger.bold(f'Maximum time is {max_time}')
            return Input.get_time_input(name, input_type, default, min_time, max_time, caller)

        return parsed

    @staticmethod
    def get_date_time_input(name: str, input_type: str = 'YYYY-mm-dd HH:MM', default: datetime = datetime.now(),
                            min_date_time: datetime = None, max_date_time: datetime = None, caller: Traceback = None):
        caller = caller if caller else getframeinfo(stack()[1][0])
        date_part = Input.get_date_input(name + 'date', default=default.date(), caller=caller)
        time_part = Input.get_time_input(name + 'time', default=default.time(), caller=caller)
        parsed = datetime.combine(date_part, time_part)

        if min_date_time and parsed < min_date_time:
            Logger.bold(f'Minimum datetime is {min_date_time}')
            return Input.get_date_time_input(name, input_type, default, min_date_time, max_date_time, caller)

        if max_date_time and parsed > max_date_time:
            Logger.bold(f'Maximum datetime is {max_date_time}')
            return Input.get_date_time_input(name, input_type, default, min_date_time, max_date_time, caller)

        return parsed
