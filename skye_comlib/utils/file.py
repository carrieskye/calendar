"""File read/write helpers."""
import csv
import json
import pickle
from pathlib import Path
from typing import Any, Dict, List, Union


class File:
    """Read and write JSON, CSV, text, and pickle files."""

    @classmethod
    def read_json(cls, path: Path) -> Union[Dict[str, Any], List[Any]]:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    @classmethod
    def write_json(cls, contents: Union[Dict[str, Any], List[Any]], path: Path) -> None:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(contents, file, indent="\t", ensure_ascii=False)

    @classmethod
    def read_txt(cls, path: Path) -> List[str]:
        with open(path, "r", encoding="utf-8") as file:
            return [x.replace("\n", "") for x in file.readlines()]

    @classmethod
    def write_txt(cls, lines: List[str], path: Path) -> None:
        with open(path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))

    @classmethod
    def read_csv(cls, path: Path) -> List[Dict[str, Any]]:
        with open(path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return [json.loads(json.dumps(row)) for row in reader]

    @classmethod
    def write_csv(cls, contents: List[Dict[str, Any]], path: Path) -> None:
        with open(path, "w", encoding="utf-8") as file:
            writer = csv.DictWriter(file, list(contents[0].keys()))
            writer.writeheader()
            writer.writerows(contents)

    @classmethod
    def read_pickle(cls, path: Path) -> Any:
        with open(path, "rb") as file:
            return pickle.load(file)

    @classmethod
    def write_pickle(cls, contents: Any, path: Path) -> None:
        with open(path, "wb") as file:
            pickle.dump(contents, file, protocol=pickle.HIGHEST_PROTOCOL)
