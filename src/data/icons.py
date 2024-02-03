from pathlib import Path
from typing import Dict

from skye_comlib.utils.file import File


class IconsDict(Dict[str, str]):
    geo_file = Path("data/icons.csv")

    def __init__(self) -> None:
        super().__init__()
        self.load_from_file()
        self.export_to_file()

    def load_from_file(self) -> None:
        for row in File.read_csv(self.geo_file):
            self[row["title"]] = row["icon"]

    def export_to_file(self) -> None:
        contents = sorted([{"title": k, "icon": v} for k, v in self.items()], key=lambda x: x["title"])
        File.write_csv(contents, self.geo_file)
