import re

from rich.highlighter import RegexHighlighter
from rich.text import Text


class CustomHighlighter(RegexHighlighter):
    def highlight(self, text: Text) -> None:
        for match in re.finditer(r"[╔╚║].*[╗╝║]", str(text)):
            text.stylize("color(75)", match.span()[0], match.span()[1])
            text.stylize("bold", match.span()[0], match.span()[1])
        for match in re.finditer(r"==+ [^=]* ==+", str(text)):
            text.stylize("color(147)", match.span()[0], match.span()[1])
            text.stylize("bold", match.span()[0], match.span()[1])
        for match in re.finditer(r"--+[^-]--+", str(text)):
            text.stylize("color(225)", match.span()[0], match.span()[1])
