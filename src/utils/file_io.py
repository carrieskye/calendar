"""JSON, CSV, text, and pickle file helpers (stdlib + pathlib)."""
import csv
import json
import pickle
from pathlib import Path
from typing import Any, Dict, List, Union


class File:
    @classmethod
    def read_json(cls, path: Path) -> Union[Dict[str, Any], List[Any]]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def write_json(cls, contents: Union[Dict[str, Any], List[Any]], path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(contents, f, indent="\t", ensure_ascii=False)

    @classmethod
    def read_txt(cls, path: Path) -> List[str]:
        with open(path, "r", encoding="utf-8") as f:
            return [x.replace("\n", "") for x in f.readlines()]

    @classmethod
    def write_txt(cls, lines: List[str], path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    @classmethod
    def read_csv(cls, path: Path) -> List[Dict[str, Any]]:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [json.loads(json.dumps(row)) for row in reader]

    @classmethod
    def write_csv(cls, contents: List[Dict[str, Any]], path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            writer = csv.DictWriter(f, list(contents[0].keys()))
            writer.writeheader()
            writer.writerows(contents)

    @classmethod
    def read_pickle(cls, path: Path) -> Any:
        with open(path, "rb") as f:
            return pickle.load(f)

    @classmethod
    def write_pickle(cls, contents: Any, path: Path) -> None:
        with open(path, "wb") as f:
            pickle.dump(contents, f, protocol=pickle.HIGHEST_PROTOCOL)
