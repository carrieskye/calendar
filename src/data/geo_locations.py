from pathlib import Path
from typing import Dict

from skye_comlib.utils.file import File

from src.models.location.geo_location import GeoLocation


class GeoLocationDict(Dict[str, GeoLocation]):
    geo_file = Path("data/geo_locations.csv")

    def __init__(self):
        super().__init__()
        self.load_from_file()

    def __add__(self, label: str, geo_location: GeoLocation):
        self[label] = geo_location
        self.export_to_file()

    def load_from_file(self):
        for geo_location in GeoLocation.build_from_csv(self.geo_file):
            self[geo_location.label] = geo_location

    def export_to_file(self):
        File.write_json(contents=[geo_location.to_dict() for geo_location in self.values()], path=self.geo_file)
