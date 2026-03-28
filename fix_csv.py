import csv
from io import StringIO
from pathlib import Path

from src.utils import File


def read_row_to_csv(row: str) -> list[str]:
    reader = csv.reader(StringIO(row))
    for line in reader:
        return line
    return []


def fix_file(path: Path) -> None:
    contents = File.read_txt(path)

    fixed_contents = []
    while contents:
        row = contents.pop(0)
        while contents and not contents[0].startswith(","):
            row += f"\\n{contents.pop(0)}"
            print(row)
        fixed_contents.append(row)

    File.write_txt(fixed_contents, path)

    csv_rows = File.read_csv(path)
    for csv_row in csv_rows:
        for k, v in csv_row.items():
            if v:
                csv_row[k] = v.replace("\\n", "\n")

    File.write_csv(csv_rows, path)


if __name__ == "__main__":
    fix_file(Path("data/child/blw.csv"))
