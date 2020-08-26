from dataclasses import dataclass

from src.data.calendars import CalendarDict
from src.data.geo_locations import GeoLocationDict


@dataclass
class Data:
    geo_location_dict = GeoLocationDict()
    calendar_dict = CalendarDict()


class GeoLocations:
    bromsgrove_st = Data.geo_location_dict['bromsgrove_st']
    talygarn_st = Data.geo_location_dict['talygarn_st']
    tramshed_tech = Data.geo_location_dict['tramshed_tech']
    viola_arena = Data.geo_location_dict['viola_arena']


class Calendars:
    chores = Data.calendar_dict['chores']
    events = Data.calendar_dict['events']
    family = Data.calendar_dict['family']
    food = Data.calendar_dict['food']
    health = Data.calendar_dict['health']
    leisure = Data.calendar_dict['leisure']
    meetings = Data.calendar_dict['meetings']
    music = Data.calendar_dict['music']
    projects = Data.calendar_dict['projects']
    school = Data.calendar_dict['school']
    shifts = Data.calendar_dict['shifts']
    social = Data.calendar_dict['social']
    sports = Data.calendar_dict['sports']
    transport = Data.calendar_dict['transport']
    trips = Data.calendar_dict['trips']
    various = Data.calendar_dict['various']
    work = Data.calendar_dict['work']
