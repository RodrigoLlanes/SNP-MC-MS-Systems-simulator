from __future__ import annotations

from random import choice
from collections import defaultdict
from typing import Callable, Iterable, Tuple, TypeVar, Generic, Dict

from utils import IdentitySet


T = TypeVar('T')


class Node(Generic[T]):
    def __init__(self) -> None:
        self._transitions: Dict[T, IdentitySet[Node]] = defaultdict(IdentitySet)

    def add_transition(self, term: T, dest: Node) -> None:
        self._transitions[term].add(dest)

    def transitions(self) -> Iterable[Tuple[T, Node]]:
        for term, destinations in self._transitions.items():
            for dest in destinations:
                yield term, dest

    def neighbours(self) -> IdentitySet[Node]:
        return IdentitySet(dest for destinations in self._transitions.values() for dest in destinations)

    def __contains__(self, key: str) -> bool:
        return key in self._transitions

    def __getitem__(self, key: str) -> Node:
        return choice(list(self._transitions[key]))


class DfaNode(Node[str]):
    def __init__(self) -> None:
        self._transitions: Dict[str, DfaNode] = {}

    def add_transition(self, term: str, dest: DfaNode) -> None:
        self._transitions[term] = dest

    def transitions(self) -> Iterable[Tuple[str, DfaNode]]:
        for term, dest in self._transitions.items():
            yield term, dest

    def neighbours(self) -> IdentitySet[DfaNode]:
        return IdentitySet(self._transitions.values())

    def __getitem__(self, key: str) -> DfaNode:
        return self._transitions[key]


def node_namer() -> Callable[[Node], Tuple[str, bool]]:
    ni = 0
    mem = {}

    def node_name(node: Node) -> Tuple[str, bool]:
        nonlocal ni
        key = id(node)
        first = key not in mem
        if first:
            mem[key] = f'q{ni}'
            ni += 1
        return mem[key], first

    return node_name
