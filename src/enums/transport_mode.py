from enum import Enum, auto


class TransportMode(Enum):
    AMBULANCE = auto()
    BUS = auto()
    CYCLING = auto()
    DRIVING = auto()
    TAXI = auto()
    TRAIN = auto()
    UNDERGROUND = auto()
    WALKING = auto()

    @classmethod
    def from_str(cls, value: str) -> "TransportMode":
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Unknown TransportMode: '{value}'")
