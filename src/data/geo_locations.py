import json
from typing import Dict

import jsonpickle

from src.models.geo_location import GeoLocation
from src.utils.file import File
from src.utils.files import Files


class GeoLocationDict(Dict[str, GeoLocation]):

    def __init__(self):
        super().__init__()
        self.load_from_file()

    def __add__(self, label: str, other: GeoLocation):
        self[label] = other
        self.export_to_file()

    def load_from_file(self):
        for label, geo_location in File.read_json(Files.geo_locations).items():
            self[label] = jsonpickle.decode(json.dumps(geo_location))

    def export_to_file(self):
        File.write_json(
            contents={label: json.loads(jsonpickle.encode(geo_location)) for label, geo_location in self.items()},
            path=Files.geo_locations
        )
