import csv
import json
import os
import pickle
from inspect import getframeinfo, stack
from typing import List, Any, Dict, Union

from src.utils.logger import Logger


class File:
    dir_name = os.path.dirname(__file__) + '/../..'

    @classmethod
    def read_json(cls, path: str, indent: int = 0, log: bool = True):
        if log:
            caller = getframeinfo(stack()[1][0])
            Logger.log(f'Reading {path}', indent, caller)
        with open(os.path.join(cls.dir_name, path), 'r') as file:
            return json.load(file)

    @classmethod
    def write_json(cls, contents: Union[Dict[str, Any], List[Any]], path: str, indent: int = 0, log: bool = True):
        if log:
            caller = getframeinfo(stack()[1][0])
            Logger.log(f'Writing {path}', indent, caller)
        with open(os.path.join(cls.dir_name, path), 'w', encoding='utf-8') as file:
            json.dump(contents, file, indent='\t', ensure_ascii=False)

    @classmethod
    def read_txt(cls, path: str, indent: int = 0, log: bool = True) -> List[str]:
        if log:
            caller = getframeinfo(stack()[1][0])
            Logger.log(f'Reading {path}', indent, caller)
        with open(os.path.join(cls.dir_name, path), 'r') as file:
            return [x.replace('\n', '') for x in file.readlines()]

    @classmethod
    def write_txt(cls, contents: List[str], path: str, sort: bool = False, indent: int = 0, log: bool = True):
        if log:
            caller = getframeinfo(stack()[1][0])
            Logger.log(f'Writing {path}', indent, caller)
        with open(os.path.join(cls.dir_name, path), 'w') as file:
            file.write('\n'.join(sorted(contents) if sort else contents))

    @classmethod
    def read_csv(cls, path: str, indent: int = 0, log: bool = True) -> List[Dict[str, Any]]:
        if log:
            caller = getframeinfo(stack()[1][0])
            Logger.log(f'Reading {path}', indent, caller)
        with open(os.path.join(cls.dir_name, path), 'r') as file:
            reader = csv.DictReader(file)
            return [json.loads(json.dumps(row)) for row in reader]

    @classmethod
    def write_csv(cls, contents: List[Dict[str, Any]], path: str, indent: int = 0, log: bool = True):
        if log:
            caller = getframeinfo(stack()[1][0])
            Logger.log(f'Writing {path}', indent, caller)
        with open(os.path.join(cls.dir_name, path), 'w') as file:
            writer = csv.DictWriter(file, contents[0].keys())
            writer.writeheader()
            writer.writerows(contents)

    @classmethod
    def read_pickle(cls, path: str, indent: int = 0, log: bool = True) -> dict:
        if log:
            caller = getframeinfo(stack()[1][0])
            Logger.log(f'Reading {path}', indent, caller)
        with open(os.path.join(cls.dir_name, path), 'rb') as file:
            return pickle.load(file)

    @classmethod
    def write_pickle(cls, contents: dict, path: str, indent: int = 0, log: bool = True):
        if log:
            caller = getframeinfo(stack()[1][0])
            Logger.log(f'Writing {path}', indent, caller)
        with open(os.path.join(cls.dir_name, path), 'wb') as file:
            pickle.dump(contents, file, protocol=pickle.HIGHEST_PROTOCOL)
