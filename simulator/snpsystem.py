import random
from collections import defaultdict
from copy import deepcopy
from typing import Dict, List, TypeVar, Generic, Set
from dataclasses import dataclass

from automatons import DFA
from utils import Multiset


T = TypeVar('T')
U = TypeVar('U')


@dataclass
class Rule(Generic[U]):
    regex: DFA
    removed: Multiset[chr]
    sent: Multiset[chr]
    chanel: U


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

    def set_input(self, inp: T) -> None:
        self._input = inp

    def set_output(self, out: T) -> None:
        self._output = out

    def add_symbols(self, neuron: T, *symbols: chr) -> None:
        self._ms[neuron].extend(symbols)

    def add_channel(self, channel: U, begin: T, end: T) -> None:
        self._channels[channel][begin].add(end)

    def add_rule(self, neuron: T, regex: str, removed: Multiset[chr], sent: Multiset[chr], chanel: U) -> None:
        self._rules[neuron].append(Rule(DFA.from_RegEx(regex), removed, sent, chanel))

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
        for target in self._channels[rule.chanel]:
            self._next_state[target].extend(rule.sent)
        return True

    def run(self, input_data: Multiset[chr]) -> Multiset[chr]:
        self._state = deepcopy(self._ms)
        self._state[self._input].extend(input_data)
        while valid_rules := self._valid_rules():
            for neuron, rules in valid_rules:
                random.shuffle(rules)
                for rule in rules:
                    self._run_rule(neuron, rule)
            self._update_state()
        return self._state[self.set_output]
