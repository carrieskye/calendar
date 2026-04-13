from enum import Enum, auto


class LocationCategory(Enum):
    # Core places
    AREA = auto()
    BEACH = auto()
    CITY = auto()
    FARM = auto()
    ISLAND = auto()
    LAKE = auto()
    LANDMARK = auto()
    LOCALITY = auto()
    MOUNTAIN = auto()
    NATURE = auto()
    PARK = auto()
    PUBLIC_SQUARE = auto()
    REGION = auto()
    TRAIL = auto()
    WATERFALL = auto()

    # Food & drink
    BAKERY = auto()
    BAR = auto()
    CAFE = auto()
    COFFEE_BAR = auto()
    FAST_FOOD = auto()
    ICE_CREAM = auto()
    PUB = auto()
    RESTAURANT = auto()

    # Retail & services
    BANK = auto()
    CAR_RENTAL = auto()
    CAR_WASH = auto()
    GARAGE = auto()
    MARKETPLACE = auto()
    PARKING = auto()
    PHARMACY = auto()
    SERVICES = auto()
    SHOPPING_CENTRE = auto()
    STORE = auto()

    # Health & care
    MEDICAL = auto()

    # Home & people
    FAMILY = auto()
    FRIENDS = auto()
    HOME = auto()
    HOUSE = auto()
    RESIDENCY = auto()

    # Travel & transport
    AIRPORT = auto()
    BUS = auto()
    FERRY = auto()
    REST_STOP = auto()
    STATION = auto()
    TERMINAL = auto()

    # Leisure & culture
    AQUARIUM = auto()
    ARENA = auto()
    CASTLE = auto()
    CHURCH = auto()
    CINEMA = auto()
    GYM = auto()
    ICE_RINK = auto()
    MUSEUM = auto()
    PLAYGROUND = auto()
    SKI_RESORT = auto()
    SPORTS = auto()
    SWIMMING_POOL = auto()
    VENUE = auto()
    YOGA_STUDIO = auto()
    ZOO = auto()

    # Work & education
    NURSERY = auto()
    SCHOOL = auto()
    UNIVERSITY = auto()
    WORK = auto()

    # Accommodation
    AIRBNB = auto()
    CAMPING = auto()
    CHALET = auto()
    HOTEL = auto()
    VACATION_HOME = auto()

    # Official buildings
    CEMETERY = auto()
    COMMUNITY_BUILDING = auto()
    CREMATORIUM = auto()
    FUNERAL_SERVICES = auto()
    GOVERNMENT = auto()
    NOTARY = auto()

    @classmethod
    def from_str(cls, value: str) -> "LocationCategory":
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Unknown LocationCategory: '{value}'")
