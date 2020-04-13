from typing import Dict


class Calendar:

    def __init__(self, key: str, original: Dict[str, str]):
        assert key in original

        self.user = original.get(key, '')
        self.partner = original.get(key + '_partner', '')
        self.shared = original.get(key + '_shared', '')
