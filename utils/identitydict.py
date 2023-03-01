from __future__ import annotations

from collections import defaultdict
from typing import TypeVar

T = TypeVar('T')


class IdentityDefaultdict:
    def __init__(self, *args, **kwargs) -> None:
        self._map = defaultdict(*args, **kwargs)
        self._keys = {}

    def __getitem__(self, key):
        self._keys[id(key)] = key
        return self._map[id(key)]

    def __setitem__(self, key, value):
        self._keys[id(key)] = key
        self._map[id(key)] = value

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return '{' + ', '.join(f'{self._keys[k]}: {v}' for k, v in self._map.items()) + '}'

    def items(self):
        for k, v in self._map.items():
            yield (self._keys[k], v)

    def keys(self):
        return self._keys.values()

    def values(self):
        return self._map.values()