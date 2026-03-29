"""JSON, CSV, and text file helpers (stdlib + pathlib)."""

import csv
import json
from pathlib import Path
from typing import Any


class File:
    @classmethod
    def read_json(cls, path: Path) -> dict[str, Any] | list[Any]:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def write_json(cls, contents: dict[str, Any] | list[Any], path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(contents, f, indent="\t", ensure_ascii=False)

    @classmethod
    def read_txt(cls, path: Path) -> list[str]:
        with open(path, encoding="utf-8") as f:
            return [x.replace("\n", "") for x in f.readlines()]

    @classmethod
    def write_txt(cls, lines: list[str], path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    @classmethod
    def read_csv(cls, path: Path) -> list[dict[str, Any]]:
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [json.loads(json.dumps(row)) for row in reader]

    @classmethod
    def write_csv(cls, contents: list[dict[str, Any]], path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            writer = csv.DictWriter(f, list(contents[0].keys()))
            writer.writeheader()
            writer.writerows(contents)
