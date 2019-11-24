import functools
import json
import re
from datetime import datetime


class Utils:

    @classmethod
    def read_json(cls, path):
        with open(path, 'r') as file:
            return json.load(file)

    @classmethod
    def write_json(cls, contents, path):
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(contents, file, indent='\t', ensure_ascii=False)

    @classmethod
    def normalise(cls, text):
        text = text.lower()
        text = text.replace('&', 'and')
        text = re.sub(r'[^\w @.]', '', text)
        return text.replace(' ', '_')

    @classmethod
    def trakt_datetime(cls, original):
        return datetime.strptime(original, '%Y-%m-%dT%H:%M:%S.%fZ')

    @classmethod
    def get_recursive_attr(cls, obj, attr, *args):
        def _get_recursive_attr(sub_obj, sub_attr):
            return getattr(sub_obj, sub_attr, *args)

        return functools.reduce(_get_recursive_attr, [obj] + attr.split('.'))
