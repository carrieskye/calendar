from enum import Enum


class TransportMode(str, Enum):
    BUS = "bus"
    CYCLING = "cycling"
    DRIVING = "driving"
    TAXI = "taxi"
    UNDERGROUND = "underground"
    WALKING = "walking"
