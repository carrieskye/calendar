from enum import Enum


class LocationCategory(str, Enum):
    # Core places
    AREA = "area"
    BEACH = "beach"
    FARM = "farm"
    ISLAND = "island"
    LAKE = "lake"
    LANDMARK = "landmark"
    LOCALITY = "locality"
    MOUNTAIN = "mountain"
    NATURE = "nature"
    PARK = "park"
    PUBLIC_SQUARE = "public_square"
    REGION = "region"
    TRAIL = "trail"
    WATERFALL = "waterfall"

    # Food & drink
    BAKERY = "bakery"
    BAR = "bar"
    CAFE = "cafe"
    COFFEE_BAR = "coffee_bar"
    FAST_FOOD = "fast_food"
    ICE_CREAM = "ice_cream"
    PUB = "pub"
    RESTAURANT = "restaurant"

    # Retail & services
    BANK = "bank"
    CAR_WASH = "car_wash"
    GARAGE = "garage"
    MARKETPLACE = "marketplace"
    PARKING = "parking"
    PHARMACY = "pharmacy"
    SERVICES = "services"
    SHOPPING_CENTRE = "shopping_centre"
    STORE = "store"

    # Health & care
    MEDICAL = "medical"

    # Home & people
    FAMILY = "family"
    FRIENDS = "friends"
    HOME = "home"
    HOUSE = "house"
    RESIDENCY = "residency"

    # Travel & transport
    AIRPORT = "airport"
    BUS = "bus"
    FERRY = "ferry"
    REST_STOP = "rest_stop"
    STATION = "station"
    TERMINAL = "terminal"

    # Leisure & culture
    AQUARIUM = "aquarium"
    ARENA = "arena"
    CASTLE = "castle"
    CHURCH = "church"
    CINEMA = "cinema"
    GYM = "gym"
    ICE_RINK = "ice_rink"
    MUSEUM = "museum"
    PLAYGROUND = "playground"
    SKI_RESORT = "ski_resort"
    SPORTS = "sports"
    SWIMMING_POOL = "swimming_pool"
    VENUE = "venue"
    YOGA_STUDIO = "yoga_studio"
    ZOO = "zoo"

    # Work & education
    NURSERY = "nursery"
    SCHOOL = "school"
    UNIVERSITY = "university"
    WORK = "work"

    # Accommodation
    AIRBNB = "airbnb"
    CAMPING = "camping"
    CHALET = "chalet"
    HOTEL = "hotel"
    VACATION_HOME = "vacation_home"

    # Official buildings
    CEMETERY = "cemetery"
    COMMUNITY_BUILDING = "community_building"
    CREMATORIUM = "crematorium"
    FUNERAL_SERVICES = "funeral_services"
    GOVERNMENT = "government"
    NOTARY = "notary"
