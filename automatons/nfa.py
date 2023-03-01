from __future__ import annotations

from collections import defaultdict

from automatons.enfa import EpsilonNFA, epsilon
from automatons.node import Node
from utils import IdentitySet, IdentityDefaultdict


class NFA(EpsilonNFA):
    @staticmethod
    def cast(automaton: EpsilonNFA) -> NFA:
        nodes = automaton.nodes()
        symbols = automaton.symbols()

        e_closure = IdentityDefaultdict(IdentitySet)
        for q0 in nodes:
            e_closure[q0].add(q0)
            stack = [q0]
            while len(stack):
                node = stack.pop()
                for nt, q1 in node.transitions():
                    if nt is epsilon and q1 not in e_closure[q0]:
                        e_closure[q0].add(q1)
                        stack.append(q1)

        delta = IdentityDefaultdict(lambda: defaultdict(IdentitySet))
        for q0 in nodes:
            for s in symbols - {epsilon, }:
                for node in e_closure[q0]:
                    for nt, q1 in node.transitions():
                        if nt == s:
                            delta[q0][s].extend(e_closure[
                                                    q1])  # TODO: con .add(q1), parece que tambien funciona y queda más bonito, pero se supone que el algoritmo es así

        new_nodes = IdentityDefaultdict(Node)
        for q0, transitions in delta.items():
            for nt, states in transitions.items():
                for q1 in states:
                    new_nodes[q0].add_transition(nt, new_nodes[q1])

        res = NFA()
        res.initial_state = new_nodes[automaton.initial_state]
        res.final_states = IdentitySet(
            [new_nodes[node] for node in nodes if len(automaton.final_states.intersection(e_closure[node]))])
        return res
