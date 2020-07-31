import math
import os
from datetime import datetime
from inspect import getframeinfo, stack, Traceback
from typing import List

from src.utils.formatter import Formatter


class Logger:
    log_file = open(f'.logs/{str(datetime.now().timestamp())}.log', 'a')
    cur_dir = os.path.dirname(os.path.abspath(__file__)).replace('src/utils', '')
    columns, _ = os.get_terminal_size(0)
    on_title = True

    @classmethod
    def title(cls, text: str):
        if not cls.on_title:
            cls.empty_line()
            cls.empty_line()

        for line in Formatter.make_title(text).split('\n'):
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f'{now}    {line}')
            cls.log_file.write(f'{now}    {line}\n')

        cls.empty_line()
        cls.on_title = True

    @classmethod
    def sub_title(cls, text: str, caller: Traceback = None):
        if not cls.on_title:
            cls.empty_line()
            cls.empty_line()
        cls.log(f'======== {text.upper()} ========', caller=caller if caller else getframeinfo(stack()[1][0]))
        cls.on_title = True

    @classmethod
    def sub_sub_title(cls, text: str, caller: Traceback = None):
        if not cls.on_title:
            cls.empty_line()
        cls.log(f'-- {text} --', caller=caller if caller else getframeinfo(stack()[1][0]))
        cls.on_title = True

    @classmethod
    def bold(cls, text: str, caller: Traceback = None):
        return cls.log(Formatter.make_bold(text), caller=caller if caller else getframeinfo(stack()[1][0]))

    @classmethod
    def empty_line(cls):
        print(cls.get_prefix())
        cls.log_file.write(f'{cls.get_prefix()}\n')

    @classmethod
    def log(cls, text: any, indent: int = 0, caller: Traceback = None, log_location: bool = True):
        if log_location and not caller:
            caller = getframeinfo(stack()[1][0])
        lines = cls.format_text(str(text), indent)
        for line in lines:
            print(f'{cls.get_prefix(caller)}    {line}')
            cls.log_file.write(f'{cls.get_prefix(caller)}    {Formatter.clear(line)}\n')
        cls.on_title = False

    @classmethod
    def format_text(cls, text: str, indent: int = 0) -> List[str]:
        lines = []
        prefix = ''.join(['    '] * indent)
        for line in text.split('\n'):
            line += ' '
            max_line_width = cls.columns - (len(prefix) + 57)
            no_sub_lines = math.ceil(len(line) / max_line_width)
            for index in range(0, no_sub_lines):
                lines.append(prefix + line[index * max_line_width: (index + 1) * max_line_width])
        return lines

    @classmethod
    def get_tqdm_desc(cls, label: str = '', indent: int = 0) -> str:
        caller = getframeinfo(stack()[1][0])
        indentation = ''.join(['    '] * indent)
        return f'{cls.get_prefix(caller)}    {indentation}{label}'

    @classmethod
    def get_prefix(cls, caller: Traceback = None) -> str:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not caller:
            return now

        location_width = 40
        line_no = caller.lineno
        file_name = caller.filename.replace(cls.cur_dir, '')
        location = f'{file_name}:{line_no}'.ljust(location_width)
        if len(location) > location_width:
            parts = location.split('/')
            while len('/'.join(parts)) > location_width and any([x != '...' for x in parts[1:-1]]):
                for index in range(1, len(parts) - 1):
                    if parts[index] != '...':
                        parts[index] = '...'
                        break
                location = '/'.join(parts).ljust(location_width)
            if len('/'.join(parts)) > location_width:
                offset = len(parts[-1]) - len('/'.join(parts[:-1])) + 2
                parts[-1] = '...' + parts[-1][offset:]
                location = '/'.join(parts).ljust(location_width)

        return f'{now}    {location}'
