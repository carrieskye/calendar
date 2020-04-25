from enum import Enum, auto
from typing import Dict


class Owner(Enum):
    carrie = auto()
    larry = auto()
    shared = auto()


class Calendar:

    def __init__(self, key: str, original: Dict[str, str]):
        assert key in original

        self.name = key

        self.carrie = original.get(key, '')
        self.larry = original.get(key + '_larry', '')
        self.shared = original.get(key + '_shared', '')

    def get_cal_id(self, owner: Owner):
        return self.__getattribute__(owner.name)
