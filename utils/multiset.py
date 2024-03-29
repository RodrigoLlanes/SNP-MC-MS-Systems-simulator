from __future__ import annotations

from collections import defaultdict
from collections.abc import MutableSet
from typing import Dict, Iterator, Iterable, TypeVar, Set

T = TypeVar('T')


class Multiset(MutableSet[T]):
    def __init__(self, iterable: Iterable[T] = ()) -> None:
        self.map: Dict[T, int] = defaultdict(int)
        self.extend(iterable)

    def __eq__(self, other):
        if set(self.map.keys()) != set(other.map.keys()):
            return False
        for k, v in self.map.items():
            if other.map[k] != v:
                return False
        return True

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return '(' + ', '.join(map(lambda x: f'{x[0]} * {x[1]}', self.map.items())) + ')'

    def __len__(self) -> int:
        return sum(self.map.values())

    def __iter__(self) -> Iterator[T]:
        for k, v in self.map.items():
            for _ in range(v):
                yield k

    def __contains__(self, x: T) -> bool:
        return x in self.map.keys()

    def __copy__(self):
        result = type(self)(self)
        return result

    def __sub__(self, other: Iterable[T]) -> Multiset[T]:
        res = type(self)(self)
        for item in other:
            res.discard(item)
        return res

    def __add__(self, other: Iterable[T]) -> Multiset[T]:
        res = type(self)(self)
        for item in other:
            res.add(item)
        return res

    def __mul__(self, other: int) -> Multiset[T]:
        res = Multiset()
        for _ in range(other):
            res.extend(self)
        return res

    def dot(self) -> str:
        res = ''
        for symbol, count in self.map.items():
            if len(symbol) > 1:
                symbol = f"'{symbol}'"
            if count == 0:
                continue
            elif count == 1:
                res += str(symbol)
            else:
                res += f'{symbol}<SUP>{count}</SUP>'
        return res

    def add(self, value: T) -> None:
        self._add(value)

    def _add(self, value: T) -> None:
        self.map[value] += 1

    def discard(self, value: T) -> None:
        self.map[value] -= 1
        if self.map[value] <= 0:
            del self.map[value]

    def extend(self, other: Iterable[T]) -> None:
        for item in other:
            self._add(item)

    def union(self, other: Iterable[T]) -> Multiset[T]:
        res = type(self)(self)
        c = defaultdict(int)
        for item in other:
            c[item] += 1
        for item, value in c.items():
            res.map[item] = max(res.map[item], value)
        return res

    def intersection(self, other: Multiset[T]) -> Multiset[T]:
        res = type(self)(self)
        for item, value in other.map.items():
            res.map[item] = min(res.map[item], value)
        return res

    def set(self) -> Set[T]:
        return set(self.map.keys())

    def count(self, symbol: T) -> int:
        if symbol not in self.map:
            return 0
        return self.map[symbol]
