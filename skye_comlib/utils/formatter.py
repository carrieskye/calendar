import re


class Formatter:
    bold_tag = "\033[1m"
    reset_tag = "\033[0;0m"

    @classmethod
    def bold(cls, text: str) -> str:
        return cls.bold_tag + text + cls.reset_tag

    @classmethod
    def title(cls, text: str) -> str:
        border = "".join(["\u2550" for _ in range(0, len(text) + 2)])
        top_border = "\u2554" + border + "\u2557"
        bottom_border = "\u255A" + border + "\u255D"
        return f"\n\n\n{top_border}\n\u2551 {text.upper()} \u2551\n{bottom_border}\n"

    @classmethod
    def sub_title(cls, text: str) -> str:
        return f"\n\n\n====== {text.upper()} ======\n"

    @classmethod
    def sub_sub_title(cls, text: str) -> str:
        return f"\n\n--{text}--\n"

    @classmethod
    def normalise(cls, text: str) -> str:
        text = text.lower()
        text = text.replace("&", "and")
        text = re.sub(r"[^\w @.]", "", text)
        return text.replace(" ", "_")

    @classmethod
    def serialise_details(cls, details: dict) -> str:
        return "\n".join([f"- {k}: {v}" for k, v in details.items()])

    @classmethod
    def de_serialise_details(cls, details: str) -> dict:
        de_serialised = {}
        for row in details.split("\n"):
            match = re.fullmatch(r"- (.*): (.*)", row)
            if match:
                k, v = match.groups()
                de_serialised[k] = v
        return de_serialised
