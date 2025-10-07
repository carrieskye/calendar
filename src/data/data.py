from src.data.calendars import CalendarDict
from src.data.geo_locations import GeoLocationDict
from src.data.icons import IconsDict
from src.data.runtime_cache import RuntimeCache


class Data:
    geo_location_dict: GeoLocationDict = GeoLocationDict()
    calendar_dict: CalendarDict = CalendarDict()
    icons_dict: IconsDict = IconsDict()
    runtime_cache: RuntimeCache = RuntimeCache()

    projects_to_ignore = [
        "Help people",
        "Food",
        "Friends",
        "Family",
        "Home studio",
        "Travel",
        "Household",
    ]


class GeoLocations:
    bromsgrove_st = Data.geo_location_dict["bromsgrove_st"]
    talygarn_st = Data.geo_location_dict["talygarn_st"]
    jarnvagsgatan = Data.geo_location_dict["järnvägsgatan_41_orsa"]
    tramshed_tech = Data.geo_location_dict["tramshed_tech"]
    viola_arena = Data.geo_location_dict["viola_arena"]


class Calendars:
    chores = Data.calendar_dict["chores"]
    family = Data.calendar_dict["family"]
    health = Data.calendar_dict["health"]
    kids = Data.calendar_dict["kids"]
    lazing = Data.calendar_dict["lazing"]
    meetings = Data.calendar_dict["meetings"]
    music = Data.calendar_dict["music"]
    projects = Data.calendar_dict["projects"]
    recreation = Data.calendar_dict["recreation"]
    school = Data.calendar_dict["school"]
    shared = Data.calendar_dict["shared"]
    shared_diary = Data.calendar_dict["shared_diary"]
    shifts = Data.calendar_dict["shifts"]
    social = Data.calendar_dict["social"]
    sports = Data.calendar_dict["sports"]
    wina = Data.calendar_dict["wina"]
    work = Data.calendar_dict["work"]
