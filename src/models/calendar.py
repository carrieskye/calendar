from enum import Enum, auto

from pydantic import BaseModel


class Owner(Enum):
    user = auto()
    partner = auto()
    shared = auto()


class Calendar(BaseModel):
    name: str
    user: str
    partner: str
    shared: str

    def get_cal_id(self, owner: Owner) -> str:
        return self.__getattribute__(owner.name)

    def get_calendars(self) -> dict[Owner, str]:
        return {
            k: v
            for k, v in {Owner.user: self.user, Owner.partner: self.partner, Owner.shared: self.shared}.items()
            if v
        }

    @classmethod
    def from_key(cls, key: str, original: dict[str, str]) -> "Calendar":
        if key not in original:
            raise ValueError(f"Key '{key}' not in original dictionary")

        return Calendar(
            name=key,
            user=original.get(key, ""),
            partner=original.get(key + "_partner", ""),
            shared=original.get(key + "_shared", ""),
        )
