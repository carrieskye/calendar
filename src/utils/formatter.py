import re


class Formatter:
    bold = '\033[1m'
    reset = '\033[0;0m'

    @classmethod
    def make_bold(cls, text: str) -> str:
        return cls.bold + text + cls.reset

    @classmethod
    def make_title(cls, text: str) -> str:
        return '\n'.join([
            u'\u2554' + ''.join([u'\u2550' for _ in range(0, len(text) + 2)]) + u'\u2557',
            u'\u2551 ' + text.upper() + u' \u2551',
            u'\u255A' + ''.join([u'\u2550' for _ in range(0, len(text) + 2)]) + u'\u255D'
        ])

    @classmethod
    def clear(cls, text: str) -> str:
        return text.replace(cls.bold, '').replace(cls.reset, '')

    @classmethod
    def normalise(cls, text):
        text = text.lower()
        text = text.replace('&', 'and')
        text = re.sub(r'[^\w @.]', '', text)
        return text.replace(' ', '_')

    @classmethod
    def serialise_details(cls, details: dict) -> str:
        return '\n'.join([f'- {k}: {v}' for k, v in details.items()])

    @classmethod
    def deserialise_details(cls, details: str) -> dict:
        de_serialised = {}
        for row in details.split('\n'):
            match = re.fullmatch(r'- (.*): (.*)', row)
            if match:
                k, v = match.groups()
                de_serialised[k] = v
        return de_serialised
