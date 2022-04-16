import csv
from io import StringIO
from pathlib import Path
from typing import List

from skye_comlib.utils.file import File


def read_row_to_csv(row: str) -> List[str]:
    reader = csv.reader(StringIO(row))
    for line in reader:
        return line


def fix_file(path: Path):
    contents = File.read_txt(path)

    fixed_contents = []
    while contents:
        row = contents.pop(0)
        while contents and not contents[0].startswith(","):
            row += f"\\n{contents.pop(0)}"
            print(row)
        fixed_contents.append(row)

    File.write_txt(fixed_contents, path)

    contents = File.read_csv(path)
    for row in contents:
        for k, v in row.items():
            if v:
                row[k] = v.replace("\\n", "\n")

    File.write_csv(contents, path)


if __name__ == "__main__":
    fix_file(Path("data/hayley/blw.csv"))
