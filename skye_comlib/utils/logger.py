import logging

from rich.logging import RichHandler

from skye_comlib.utils.custom_highlighter import CustomHighlighter


class Logger:
    @staticmethod
    def configure() -> None:
        rich_handler = RichHandler(highlighter=CustomHighlighter())
        rich_handler.KEYWORDS = []
        logging.basicConfig(level=logging.INFO, format="%(message)s", datefmt="[%X]", handlers=[rich_handler])

    @staticmethod
    def get_prefix() -> str:
        return "                    "
