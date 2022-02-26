import json
from typing import Dict

import jsonpickle
from skye_comlib.utils.file import File

from src.models.geo_location import GeoLocation


class GeoLocationDict(Dict[str, GeoLocation]):
    geo_file = "data/geo_locations.json"

    def __init__(self):
        super().__init__()
        self.load_from_file()

    def __add__(self, label: str, other: GeoLocation):
        self[label] = other
        self.export_to_file()

    def load_from_file(self):
        for label, geo_location in File.read_json(self.geo_file).items():
            self[label] = jsonpickle.decode(json.dumps(geo_location))

    def export_to_file(self):
        File.write_json(
            contents={
                label: json.loads(jsonpickle.encode(geo_location))
                for label, geo_location in self.items()
            },
            path=self.geo_file,
        )
