from typing import Dict


class Calendar:

    def __init__(self, key: str, original: Dict[str, str]):
        assert key in original

        self.carrie = original.get(key, '')
        self.larry = original.get(key + '_larry', '')
        self.shared = original.get(key + '_shared', '')
