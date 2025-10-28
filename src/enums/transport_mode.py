from enum import Enum


class TransportMode(str, Enum):
    AMBULANCE = "ambulance"
    BUS = "bus"
    CYCLING = "cycling"
    DRIVING = "driving"
    TAXI = "taxi"
    TRAIN = "train"
    UNDERGROUND = "underground"
    WALKING = "walking"
