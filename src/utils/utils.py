import csv
import functools
import json
import os
import pickle
import re
from datetime import datetime
from typing import Any, List, Dict, Counter


class Utils:
    dir_name = os.path.dirname(__file__) + '/../..'

    @classmethod
    def read_json(cls, path: str, indent: int = 0, log: bool = False) -> Dict[str, Any]:
        if log:
            cls.log(f'Reading {path}', indent)
        with open(os.path.join(cls.dir_name, path), 'r') as file:
            return json.load(file)

    @classmethod
    def write_json(cls, contents: Dict[str, Any], path: str, indent: int = 0, log: bool = False):
        if log:
            cls.log(f'Writing {path}', indent)
        with open(os.path.join(cls.dir_name, path), 'w', encoding='utf-8') as file:
            json.dump(contents, file, indent='\t', ensure_ascii=False)

    @classmethod
    def read_csv(cls, path: str, indent: int = 0, log: bool = False) -> List[Dict[str, Any]]:
        if log:
            cls.log(f'Reading {path}', indent)
        with open(os.path.join(cls.dir_name, path), 'r') as file:
            reader = csv.DictReader(file)
            return [json.loads(json.dumps(row)) for row in reader]

    @classmethod
    def write_csv(cls, contents: List[Dict[str, Any]], path: str, indent: int = 0, log: bool = False):
        if log:
            cls.log(f'Writing {path}', indent)
        with open(os.path.join(cls.dir_name, path), 'w') as file:
            writer = csv.DictWriter(file, contents[0].keys())
            writer.writeheader()
            writer.writerows(contents)

    @classmethod
    def read_txt(cls, path: str, indent: int = 0, log: bool = False) -> List[str]:
        if log:
            cls.log(f'Reading {path}', indent)
        with open(os.path.join(cls.dir_name, path), 'r') as file:
            return [x.replace('\n', '') for x in file.readlines()]

    @classmethod
    def write_txt(cls, contents: List[str], path: str, sort: bool = False, indent: int = 0, log: bool = False):
        if log:
            cls.log(f'Writing {path}', indent)
        with open(os.path.join(cls.dir_name, path), 'w') as file:
            file.write('\n'.join(sorted(contents) if sort else contents))

    @classmethod
    def read_pickle(cls, path: str, indent: int = 0, log: bool = False) -> Counter:
        if log:
            cls.log(f'Reading {path}', indent)
        with open(os.path.join(cls.dir_name, path), 'rb') as file:
            return pickle.load(file)

    @classmethod
    def write_pickle(cls, contents: Counter, path: str, indent: int = 0, log: bool = False):
        if log:
            cls.log(f'Writing {path}', indent)
        with open(os.path.join(cls.dir_name, path), 'wb') as file:
            pickle.dump(contents, file)

    @classmethod
    def log(cls, text: str, indent: int = 0):
        for line in text.split('\n'):
            print(''.join(['    '] * indent) + line)

    @classmethod
    def input(cls, text: str) -> str:
        lines = text.split('\n')
        for line in lines[:-1]:
            cls.log(line)
        return input(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\t {lines[-1]}')

    @classmethod
    def get_percentage(cls, part: int, total: int) -> str:
        return f'{(100 * part / total):.2f} %'

    @classmethod
    def log_percentage(cls, part: int, total: int, label: str = '', indent: int = 0):
        width = len(str(total)) * 2 + 3
        fraction = f'{part} / {total}'.rjust(width)
        percentage = cls.get_percentage(part, total).rjust(10)
        cls.log(f'{fraction} {percentage}   {label}', indent=indent)

    @classmethod
    def get_tqdm_desc(cls, label: str = '', indent: int = 0) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S      ') + ''.join(['    '] * indent) + label

    @classmethod
    def normalise(cls, text):
        text = text.lower()
        text = text.replace('&', 'and')
        text = re.sub(r'[^\w @.]', '', text)
        return text.replace(' ', '_')

    @classmethod
    def trakt_datetime(cls, original):
        return datetime.strptime(original, '%Y-%m-%dT%H:%M:%S.%fZ')

    @classmethod
    def get_recursive_attr(cls, obj, attr, *args):
        def _get_recursive_attr(sub_obj, sub_attr):
            return getattr(sub_obj, sub_attr, *args)

        return functools.reduce(_get_recursive_attr, [obj] + attr.split('.'))
