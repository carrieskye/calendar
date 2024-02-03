from typing import List

from prettytable import PrettyTable

from src.data.data import Data
from src.scripts.location.location import LocationScript


class PrintLocations(LocationScript):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None:
        data: List[dict] = []
        table = PrettyTable(align="l")
        for geo_location in Data.geo_location_dict.values():
            new_dict = {**geo_location.__dict__, **geo_location.address.__dict__}
            new_dict.pop("address")
            new_dict.pop("time_zone")
            new_dict.pop("original")
            new_dict.pop("short")
            new_dict.pop("state")
            new_dict.pop("country_code")
            new_dict["address_lines"] = ", ".join(new_dict["address_lines"])
            if len(new_dict["address_lines"]) > 80:
                new_dict["address_lines"] = new_dict["address_lines"][:80]

            data.append(new_dict)
        table.field_names = list(data[0].keys())
        for row in data:
            table.add_row(list(row.values()))
        print(table)
