from __future__ import annotations

from copy import deepcopy
from collections import defaultdict
from typing import Union, Dict, Optional, Tuple, TypeVar, Set

from automatons.node import Node, node_namer
from utils import IdentitySet, clossing_index

epsilon = None
RLGProductions = Optional[Union[Tuple[str, str], Tuple[str]]]
RLG = Dict[str, Set[RLGProductions]]


class EpsilonNFA:
    def __init__(self, empty: bool = True) -> None:
        self.initial_state: Node = Node()
        self.final_states: IdentitySet[Node] = IdentitySet()
        if not empty:
            self.final_states.add(self.initial_state)

    def symbols(self) -> set[str]:
        res = set()
        visited = IdentitySet([self.initial_state])
        stack = [self.initial_state]
        while len(stack):
            for nt, n in stack.pop().transitions():
                res.add(nt)
                if n not in visited:
                    visited.add(n)
                    stack.append(n)
        return res

    def nodes(self) -> IdentitySet[Node]:
        visited = IdentitySet([self.initial_state])
        stack = [self.initial_state]
        while len(stack):
            for _, n in stack.pop().transitions():
                if n not in visited:
                    visited.add(n)
                    stack.append(n)
        return visited

    def render_dot(self) -> str:
        nodes = ['node [shape = point]; qi']
        edges = ['qi -> q0;']

        edges_names = defaultdict(set)
        node_name = node_namer()
        stack = [self.initial_state]
        while len(stack):
            node = stack.pop(0)
            name, _ = node_name(node)
            nodes.append(
                f'node [shape = {"circle" if node not in self.final_states else "doublecircle"}, label = "{name}"]; {name}')
            for nt, n in node.transitions():
                n_name, first = node_name(n)
                nt = nt if nt is not None else 'ɛ'
                edges_names[name, n_name].add(nt)
                if first:
                    stack.append(n)
        for (q0, q1), symbs in edges_names.items():
            edges.append(f'{q0} -> {q1} [label = "{", ".join(symbs)}"];')
        return 'digraph graph_rendered{\n    ' + '\n    '.join(nodes + edges) + '\n}'

    @staticmethod
    def cast(automata: EpsilonNFA) -> EpsilonNFA:
        return automata

    @classmethod
    def combine(cls, a: EpsilonNFA, b: EpsilonNFA, copy: bool = True) -> EpsilonNFA:
        ac = deepcopy(a) if copy else a
        bc = deepcopy(b) if copy else b
        for state in ac.final_states:
            state.add_transition(epsilon, bc.initial_state)
        ac.final_states = bc.final_states
        return cls.cast(ac)

    @classmethod
    def from_RLG(cls, grammar: RLG, s: str) -> EpsilonNFA:
        nodes = defaultdict(Node)
        final = 0
        final_states = IdentitySet([nodes[final]])
        states = {final, s}
        unknown = [s]

        while len(unknown):
            current = unknown.pop()
            for prod in grammar[current]:
                if prod is None:
                    final_states.add(nodes[current])
                elif len(prod) == 1:
                    symbol = prod[0]
                    nodes[current].add_transition(symbol, nodes[final])
                else:
                    state, symbol = prod
                    nodes[current].add_transition(symbol, nodes[state])
                    if state not in states:
                        states.add(state)
                        unknown.append(state)
        enfa = EpsilonNFA()
        enfa.initial_state = nodes[s]
        enfa.final_states = final_states
        return cls.cast(enfa)

    @classmethod
    def from_RegEx(cls, regex: str) -> EpsilonNFA:
        return cls.cast(cls._from_RegEx(regex))

    @staticmethod
    def _from_RegEx(regex: str) -> EpsilonNFA:
        if not len(regex):
            return EpsilonNFA(empty=False)
        elif len(regex) == 1:
            res = EpsilonNFA()
            final = Node()
            res.initial_state.add_transition(regex, final)
            res.final_states.add(final)
            return res
        elif regex[0] == '(':
            i = clossing_index(regex)
            left = EpsilonNFA.from_RegEx(regex[1:i])
            if regex[i + 1] == '*':
                for final in left.final_states:
                    final.add_transition(epsilon, left.initial_state)
                left.final_states.add(left.initial_state)
                right = EpsilonNFA.from_RegEx(regex[i + 2:])
            elif regex[i + 1] == '+':
                for final in left.final_states:
                    final.add_transition(epsilon, left.initial_state)
                right = EpsilonNFA.from_RegEx(regex[i + 2:])
            else:
                right = EpsilonNFA.from_RegEx(regex[i + 1:])
            return EpsilonNFA.combine(left, right)
        elif regex[1] == '*':
            left = EpsilonNFA(empty=False)
            left.initial_state.add_transition(regex[0], left.initial_state)
            right = EpsilonNFA.from_RegEx(regex[2:])
            return EpsilonNFA.combine(left, right)
        elif regex[1] == '+':
            left = EpsilonNFA()
            final = Node()
            left.initial_state.add_transition(regex[0], final)
            final.add_transition(regex[0], final)
            left.final_states.add(final)
            right = EpsilonNFA.from_RegEx(regex[2:])
            return EpsilonNFA.combine(left, right)
        else:
            left = EpsilonNFA()
            final = Node()
            left.initial_state.add_transition(regex[0], final)
            left.final_states.add(final)
            right = EpsilonNFA.from_RegEx(regex[1:])
            return EpsilonNFA.combine(left, right)
