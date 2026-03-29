"""Rich-backed logging setup (replaces custom Logger + ANSI-only handlers)."""

import logging

from rich.logging import RichHandler


def configure_logging() -> None:
    handler = RichHandler(rich_tracebacks=True, markup=True)
    handler.KEYWORDS = []
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[handler],
        force=True,
    )
