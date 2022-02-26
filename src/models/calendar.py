from enum import Enum, auto
from typing import Dict


class Owner(Enum):
    user = auto()
    partner = auto()
    shared = auto()


class Calendar:
    def __init__(self, key: str, original: Dict[str, str]):
        assert key in original

        self.name = key

        self.user = original.get(key, "")
        self.partner = original.get(key + "_partner", "")
        self.shared = original.get(key + "_shared", "")

    def get_cal_id(self, owner: Owner):
        return self.__getattribute__(owner.name)

    def get_calendars(self):
        return {
            k: v
            for k, v in {
                Owner.user: self.user,
                Owner.partner: self.partner,
                Owner.shared: self.shared,
            }.items()
            if v
        }
