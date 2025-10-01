from enum import Enum


class TransportMode(str, Enum):
    BUS = "bus"
    CYCLING = "cycling"
    DRIVING = "driving"
    TAXI = "taxi"
    TRAIN = "train"
    UNDERGROUND = "underground"
    WALKING = "walking"
