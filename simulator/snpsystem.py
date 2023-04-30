from __future__ import annotations

import random
from collections import defaultdict
from copy import deepcopy
from typing import Dict, List, TypeVar, Generic, Set
from dataclasses import dataclass
from graphviz import Digraph
import numpy as np
import matplotlib.pyplot as plt

from automatons import DFA
from utils import Multiset

T = TypeVar('T')
U = TypeVar('U')


@dataclass
class Rule(Generic[U]):
    regex_str: str
    regex: DFA
    removed: Multiset[chr]
    channels: Dict[U, Multiset[chr]]

    def __str__(self):
        return f'{self.regex_str} / {self.removed} --> ' + \
            ', '.join(f'{content} <{channel}>' for channel, content in self.channels.items())


def register_membrane(*indexes):
    def decorator(f):
        def wrapper(self: SNPSystem, *args, **kwargs):
            for i in indexes:
                self.add_symbols(args[i])
            return f(self, *args, **kwargs)

        return wrapper

    return decorator


class SNPSystem(Generic[T, U]):
    """
    T: Neuron id type
    U: Chanel id type
    """

    def __init__(self) -> None:
        self._input: T = None
        self._output: T = None
        self._ms: Dict[T, Multiset[chr]] = defaultdict(Multiset)
        self._channels: Dict[U, Dict[T, Set[T]]] = defaultdict(lambda: defaultdict(set))
        self._rules: Dict[int, List[Rule]] = defaultdict(list)

        self._state: Dict[T, Multiset[chr]] = {}
        self._next_state: Dict[T, Multiset[chr]] = {}

    def draw(self):
        dot = Digraph()

        for node, content in self._ms.items():
            rules = '\n'.join(map(str, self._rules[node]))
            dot.node(str(node), f'{node}\n{str(content)}\n' + rules)

        for channel, content in self._channels.items():
            for start, ends in content.items():
                for end in ends:
                    dot.edge(str(start), str(end), str(channel))

        dot.render(view=True)

    @register_membrane(0)
    def set_input(self, inp: T) -> None:
        self._input = inp

    @register_membrane(0)
    def set_output(self, out: T) -> None:
        self._output = out

    def add_symbols(self, neuron: T, *symbols: chr) -> None:
        self._ms[neuron].extend(symbols)

    @register_membrane(1, 2)
    def add_channel(self, channel: U, begin: T, end: T) -> None:
        self._channels[channel][begin].add(end)

    @register_membrane(0)
    def add_rule(self, neuron: T, regex: str, removed: Multiset[chr], channels: Dict[U, Multiset[chr]]) -> None:
        self._rules[neuron].append(Rule(regex, DFA.from_RegEx(regex), removed, channels))

    def _update_state(self):
        self._state = deepcopy(self._next_state)

    def _valid_rules(self) -> Dict[T, List[Rule]]:
        return {
            neuron: [rule
                     for rule in rules
                     if rule.regex.accepts_multiset(self._state[neuron])]
            for neuron, rules in self._state.items()
        }

    def _run_rule(self, neuron: T, rule: Rule) -> bool:
        if rule.removed not in self._state[neuron]:
            return False

        self._next_state[neuron].discard(rule.removed)
        for channel, sent in rule.channels.items():
            for target in self._channels[channel]:
                self._next_state[target].extend(sent)
        return True

    def run(self, input_data: Multiset[chr]) -> Multiset[chr]:
        self._state = deepcopy(self._ms)
        self._state[self._input].extend(input_data)
        while valid_rules := self._valid_rules():  # Esto esta mal
            for neuron, rules in valid_rules:  # Para cada neurona se crea una pool de reglas aplicables
                random.shuffle(
                    rules)  # Cada vez que se aplica una regla, se comprueba en un map que reglas dependían de alguno de esos símbolos
                for rule in rules:  # Si ya no se puede aplicar, se elimina a si misma de la pool
                    self._run_rule(neuron,
                                   rule)  # Repetir hasta que la pool esté vacía, notese que lo que se envía se almacena en una pool de outputs, lo que se elimina si que se puede eliminar del estado
            self._update_state()
        return self._state[self.set_output]
