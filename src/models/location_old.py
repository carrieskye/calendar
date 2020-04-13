# from math import radians, atan2, sin, cos, sqrt
#
# from src.utils.utils import Utils
#
# TIME_ZONES = Utils.read_json('data/google/time_zones.json')
#
#
# class Location:
#
#     def __init__(self, name: str, latitude: float, longitude: float, radius: int, time_zone: str):
#         self.name = name
#         self.latitude = latitude
#         self.longitude = longitude
#         self.radius = radius
#         self.time_zone = time_zone
#
#     @staticmethod
#     def get_distance(lat_1, lon_1, lat_2, lon_2):
#         earth_radius = 6371e3
#         phi_1 = radians(lat_1)
#         phi_2 = radians(lat_2)
#         df = radians(lat_2 - lat_1)
#         dl = radians(lon_2 - lon_1)
#
#         a = sin(df / 2) * sin(df / 2) + cos(phi_1) * cos(phi_2) * sin(dl / 2) * sin(dl / 2)
#         c = 2 * atan2(sqrt(a), sqrt(1 - a))
#
#         return earth_radius * c
#
#
# class IndependentLocation(Location):
#
#     def __init__(self, name: str, latitude: float, longitude: float, radius: int, address: str):
#         self.address = address
#         super().__init__(name, latitude, longitude, radius, get_time_zone(address))
#
#
# class LocationGroup:
#
#     def __init__(self, location: IndependentLocation, max_distance: int):
#         self.location = location
#         self.max_distance = max_distance
#
#
# class SubLocation(Location):
#
#     def __init__(self, name: str, latitude: float, longitude: float, radius: int, group: LocationGroup):
#         self.group = group
#         super().__init__(name, latitude, longitude, radius, get_time_zone(group.location.address))
#
#
# def get_time_zone(address):
#     return TIME_ZONES[address.split(', ')[-1]]
