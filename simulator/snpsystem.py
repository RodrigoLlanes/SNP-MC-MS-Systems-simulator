from __future__ import annotations

import random
import re
import typing
from collections import defaultdict
from copy import deepcopy
from typing import Dict, List, TypeVar, Generic, Set, Optional, Tuple
from dataclasses import dataclass
from utils.graphrenderer import GraphRenderer

from automatons import DFA
from utils import Multiset

T = TypeVar('T')
U = TypeVar('U')


class Rule:
    def __init__(self, regex: Optional[typing.Union[str, List[str]]], removed: Multiset[str], channels: Dict[U, Multiset[str]], block: int):
        self.regex_str: Optional[str] = regex
        self.regex: DFA = DFA.from_RegEx(regex) if regex else None
        self.removed: Multiset[str] = removed
        self.channels: Dict[str, Multiset[str]] = channels
        self.forgetting: bool = len(channels) == 0
        self.block: int = block

    def __str__(self):
        synapses = ', '.join(f'{content} <{channel}>' for channel, content in self.channels.items())
        if self.forgetting:
            synapses = 'λ'
        block = '' if self.block == 0 else f' ; {self.block}'

        if self.regex:
            return f'{self.regex_str} / {self.removed} --> {synapses}{block}'
        else:
            return f'{self.removed} --> {synapses}{block}'

    def __repr__(self):
        return str(self)

    def valid(self, multiset: Multiset[str]) -> bool:
        if self.forgetting:
            return True
        elif self.regex is None:
            return self.removed == multiset
        else:
            return self.regex.accepts_multiset(multiset)

    def dot(self):
        regex = self.regex_str
        if regex is not None:
            if isinstance(regex, list):
                regex = ''.join(s if len(s) == 1 else f"'{s}'" for s in regex)
            regex = re.sub(r'\+', '<SUP>+</SUP>', regex)
            regex = re.sub(r'\*', '<SUP>*</SUP>', regex)

        synapses = ', '.join(f'{content.dot()} ({channel})' for channel, content in self.channels.items())
        if self.forgetting:
            synapses = 'λ'
        block = '' if self.block == 0 else f' ; {self.block}'

        if self.regex:
            return f'{regex} / {self.removed.dot()} → {synapses}{block}'
        else:
            return f'{self.removed.dot()} → {synapses}{block}'


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
        self._delay: Dict[T, List[int, Optional[Rule]]] = {}
        self._next_state: Dict[T, Multiset[chr]] = {}

        self._history: List[Dict[str, Multiset]] = []

    def render(self, path, current_state: bool = False, name: str = 'SNP-System', comment: str = ''):
        gr = GraphRenderer(name, comment=comment)

        for node in self._ms.keys():
            rules = '<BR/>'.join(map(lambda x: x.dot(), self._rules[node]))
            content = self._ms[node] if not current_state else self._state[node]
            gr.add_node(str(node), f'<{content.dot()}<BR/>{rules}>', final=(node == self._output), initial=(node == self._input))

        for channel, content in self._channels.items():
            for start, ends in content.items():
                for end in ends:
                    gr.add_edge(str(start), str(end), f'{channel}')

        gr.render(path)

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
    def add_rule(self, neuron: T, regex: str, removed: Multiset[chr], channels: Dict[U, Multiset[chr]], block: int = 0) -> None:
        self._rules[neuron].append(Rule(regex, removed, channels, block))

    def _update_state(self):
        self._state = deepcopy(self._next_state)

    def _valid_rules(self, neuron: T) -> List[Rule]:
        return [rule for rule in self._rules[neuron] if len(rule.removed - self._state[neuron]) == 0 and rule.valid(self._state[neuron])]

    def _run_rule(self, neuron: T, rule: Rule) -> bool:
        self._state[neuron] -= rule.removed
        self._next_state[neuron] -= rule.removed
        for channel, sent in rule.channels.items():
            for target in self._channels[channel][neuron]:
                self._next_state[target].extend(sent)
                if target == self._output:
                    self._history[-1][channel].extend(sent)
        return True

    def _run_neuron(self, neuron: T) -> bool:
        modified = False

        if self._delay[neuron][0] > 0:
            self._delay[neuron][0] -= 1
            return True
        elif self._delay[neuron][0] == 0:
            self._delay[neuron][0] -= 1
            modified |= self._run_rule(neuron, self._delay[neuron][1])

        delay = 0
        while valid_rules := self._valid_rules(neuron):
            rules = [rule for rule in valid_rules if not rule.forgetting]
            if len(rules) == 0:
                rules = valid_rules

            rule = random.choice(rules)
            if rule.block > 0:
                self._delay[neuron] = [delay, rule]
                return True

            while len(rule.removed - self._state[neuron]) == 0 and rule.valid(self._state[neuron]):
                modified |= self._run_rule(neuron, rule)
        return modified

    def run(self, input_data: Multiset[str], render_steps: bool = False, render_name: str = 'SNP-System',
            render_path: str = '../tmp', mode: str = 'halt', max_steps: Optional[int] = None) -> \
            typing.Union[Multiset[str], Dict[str, Multiset[str]], List[Multiset[str]], List[Dict[str, Multiset[str]]]]:
        self._history = []
        self._next_state = deepcopy(self._ms)
        self._delay = {k: [-1, None] for k in self._ms.keys()}
        if self._input is not None:
            self._next_state[self._input].extend(input_data)
        self._update_state()
        step = 0
        if render_steps:
            self.render(render_path, True, f'{render_name}.0')
        while True:
            self._history.append(defaultdict(Multiset))
            step += 1
            modified = False
            for neuron in self._ms.keys():
                modified |= self._run_neuron(neuron)
            if not modified:
                break
            self._update_state()
            if render_steps:
                self.render(render_path, True, f'{render_name}.{step}')
            if max_steps and step == max_steps:
                break
        self._update_state()

        if self._output is not None:
            match mode:
                case 'halt':
                    return self._state[self._output]
                case 'halt-mc':
                    res = defaultdict(Multiset)
                    for item in self._history:
                        for k, v in item.items():
                            res[k].extend(v)
                    return res
                case 'time':
                    res = [Multiset() for _ in range(len(self._history))]
                    for i, item in enumerate(self._history):
                        for k, v in item.items():
                            res[i].extend(v)
                    return res
                case 'time-mc':
                    return self._history
        return Multiset()
