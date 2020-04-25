from dataclasses import dataclass

from src.data.calendars import CalendarDict
from src.data.geo_locations import GeoLocationDict


@dataclass
class Data:
    geo_location_dict = GeoLocationDict()
    calendar_dict = CalendarDict()


class GeoLocations:
    bromsgrove_st = Data.geo_location_dict['bromsgrove_st']
    tramshed_tech = Data.geo_location_dict['tramshed_tech']
    viola_arena = Data.geo_location_dict['viola_arena']


class Calendars:
    events_and_meetups = Data.calendar_dict['events_and_meetups']
    food = Data.calendar_dict['food']
    leisure = Data.calendar_dict['leisure']
    medical = Data.calendar_dict['medical']
    meetings = Data.calendar_dict['meetings']
    projects = Data.calendar_dict['projects']
    school = Data.calendar_dict['school']
    sports = Data.calendar_dict['sports']
    social = Data.calendar_dict['social']
    transport = Data.calendar_dict['transport']
    trips = Data.calendar_dict['trips']
    various = Data.calendar_dict['various']
    work = Data.calendar_dict['work']
