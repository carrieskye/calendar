"""Rich tables for debug / inspection output."""

from collections.abc import Iterable, Sequence

from rich.console import Console
from rich.table import Table


def print_data_table(
    title: str,
    headers: Sequence[str],
    column_widths: Sequence[int],
    rows: Iterable[Sequence[object]],
) -> None:
    table = Table(title=title, header_style="bold")
    for header, width in zip(headers, column_widths):
        table.add_column(header, width=width)
    for row in rows:
        table.add_row(*["" if c is None else str(c) for c in row])
    Console().print(table)
