from enum import Enum, auto
from typing import Dict

from pydantic import BaseModel


class Owner(Enum):
    carrie = auto()
    larry = auto()
    shared = auto()


class Calendar(BaseModel):
    name: str
    carrie: str
    larry: str
    shared: str

    def get_cal_id(self, owner: Owner) -> str:
        return self.__getattribute__(owner.name)

    def get_calendars(self) -> Dict[Owner, str]:
        return {
            k: v
            for k, v in {Owner.carrie: self.carrie, Owner.larry: self.larry, Owner.shared: self.shared}.items()
            if v
        }

    @classmethod
    def from_key(cls, key: str, original: Dict[str, str]) -> "Calendar":
        if key not in original:
            raise ValueError(f"Key '{key}' not in original dictionary")

        return Calendar(
            name=key,
            carrie=original.get(key, ""),
            larry=original.get(key + "_larry", ""),
            shared=original.get(key + "_shared", ""),
        )
