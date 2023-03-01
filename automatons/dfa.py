from __future__ import annotations

from collections import defaultdict
from heapq import heappush, heappop
from typing import List, Tuple, Union, Iterator

from automatons.nfa import NFA
from automatons.node import DfaNode
from automatons.enfa import EpsilonNFA
from utils import IdentitySet, IdentityFrozenSet, Multiset


class DFA(NFA):
    def __init__(self, empty: bool = True) -> None:
        self.initial_state: DfaNode = DfaNode()
        self.final_states: IdentitySet = IdentitySet()
        if not empty:
            self.final_states.add(self.initial_state)
        self.consistent: bool = self.is_consistent()

    def is_consistent(self) -> bool:
        finals = IdentitySet()
        visited = IdentitySet()
        stack = [self.initial_state]

        while len(stack):
            state = stack.pop()
            neighbours = state.neighbours()
            future = neighbours - visited
            for neighbour in future:
                visited.add(neighbour)
                stack.append(neighbour)
            if state in self.final_states or len(neighbours.intersection(finals)) > 0:
                finals.add(state)
                continue
            if len(future) > 0:
                continue
            return False
        return True

    def words_iterator(self) -> Iterator[str]:
        nodes: List[Tuple[str, DfaNode]] = [('', self.initial_state)]
        while len(nodes):
            string, state = nodes.pop(0)
            if state in self.final_states:
                yield string
            for symbol, target in state.transitions():
                nodes.append((symbol + string, target))

    def evaluate(self, word: Union[List[str], str]) -> float:
        current = self.initial_state
        for i, symbol in enumerate(word):
            if symbol not in current:
                return i / len(word)
            current = current[symbol]
        return 1 if current in self.final_states else 1 - 1 / ((len(word) + 1) * 2)

    def accepts(self, word: Union[List[str], str]) -> bool:
        return self.evaluate(word) == 1

    def accepts_multiset(self, word: Multiset) -> bool:
        symbols = tuple(word.set())
        state = tuple(word.count(s) for s in symbols)
        heap = [(0, state, self.initial_state)]
        visited = set()
        while len(heap):
            length, state, node = heappop(heap)
            if state in visited:
                continue
            else:
                visited.add(state)

            if sum(state) == 0 and node in self.final_states:
                return True

            for s, c in zip(symbols, state):
                if c > 0 and s in node:
                    new_state = tuple(nc-1 if ns == s else nc for ns, nc in zip(symbols, state))
                    heappush(heap, (length+1, new_state, node[s]))
        return False

    @staticmethod
    def cast(enfa: EpsilonNFA) -> DFA:
        nfa = NFA.cast(enfa)
        states = set()
        final_states = set()
        new_nodes = defaultdict(DfaNode)
        unknown = [IdentityFrozenSet([nfa.initial_state])]
        while len(unknown):
            q = unknown.pop()
            states.add(q)
            if len(q.intersection(nfa.final_states)):
                final_states.add(q)

            transitions = defaultdict(IdentitySet)
            for state in q:
                for k, v in state.transitions():
                    transitions[k].add(v)

            transitions = {k: IdentityFrozenSet(v) for k, v in transitions.items()}
            for k, v in transitions.items():
                new_nodes[q].add_transition(k, new_nodes[v])
                if v not in states:
                    unknown.append(v)
        dfa = DFA()
        dfa.initial_state = new_nodes[IdentityFrozenSet([nfa.initial_state])]
        dfa.final_states = IdentitySet(new_nodes[n] for n in final_states)
        return dfa