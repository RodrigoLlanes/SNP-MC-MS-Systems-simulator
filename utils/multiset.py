from __future__ import annotations

from collections import defaultdict
from collections.abc import MutableSet
from typing import Dict, Iterator, Iterable, TypeVar, Set

T = TypeVar('T')


class Multiset(MutableSet[T]):
    def __init__(self, iterable: Iterable[T] = ()) -> None:
        self.map: Dict[T, int] = defaultdict(int)
        self.extend(iterable)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return '(' + ', '.join(map(lambda x: ', '.join([str(x[0])] * x[1]), self.map.items())) + ')'

    def __len__(self) -> int:
        return sum(self.map.values())

    def __iter__(self) -> Iterator[T]:
        for k, v in self.map:
            for _ in range(v):
                yield k

    def __contains__(self, x: T) -> bool:
        return x in self.map.keys()

    def __deepcopy__(self, memo: dict) -> Multiset[T]:
        new = type(self)()
        memo[id(new)] = new
        for v in self.map.values():
            new._add(v)
        return new

    def __sub__(self, other: Iterable[T]) -> Multiset[T]:
        res = type(self)(self)
        for item in other:
            res.discard(item)
        return res

    def add(self, value: T) -> None:
        self._add(value)

    def _add(self, value: T) -> None:
        self.map[value] += 1

    def discard(self, value: T) -> None:
        if self.map[value] > 0:
            self.map[value] -= 1

    def extend(self, other: Iterable[T]) -> None:
        for item in other:
            self._add(item)

    def union(self, other: Iterable[T]) -> Multiset[T]:
        res = type(self)(self)
        res.extend(other)
        return res

    def intersection(self, other: Multiset[T]) -> Multiset[T]:
        res = type(self)()
        for item, value in other.map.items():
            res.map[item] = min(res.map[item], value)
        return res

    def set(self) -> Set[T]:
        return set(self.map.keys())

    def count(self, symbol: T):
        if symbol not in self.map:
            return 0
        return self.map[symbol]
