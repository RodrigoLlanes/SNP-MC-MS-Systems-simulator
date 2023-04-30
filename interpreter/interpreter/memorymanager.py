from __future__ import annotations

from collections import defaultdict
from copy import copy
from enum import Flag, auto
from typing import Dict, Tuple, List, Optional
from abc import ABC, abstractmethod
from interpreter.errormanager import error

from utils import Multiset


class DataType(Flag):
    INT = auto()
    SYMBOL = auto()
    MULTISET = auto()
    FUNCTION = auto()
    CHANNEL = auto()
    REGEX = auto()
    NONE = auto()
    ERROR = auto()


class Data(ABC):
    @property
    @abstractmethod
    def value(self) -> object:
        pass

    @property
    @abstractmethod
    def type(self) -> DataType:
        pass

    @property
    @abstractmethod
    def reference(self) -> Optional[str]:
        pass


class Value(Data):
    def __init__(self, value: object, t: DataType):
        self._value = value
        self._type = t

    @property
    def value(self) -> object:
        return self._value

    @value.setter
    def value(self, value: Data) -> None:
        error('MemoryManager', 'UnexpectedError', 'Trying to set value of a non variable object')

    @property
    def type(self) -> DataType:
        return self._type

    @property
    def reference(self) -> Optional[str]:
        return None


none = Value(None, DataType.NONE)


class Variable(Data):
    def __init__(self, manager: MemoryManager, reference: str):
        self._manager = manager
        self._reference = reference

    @property
    def value(self) -> object:
        return self._manager.get_var(self._reference)

    @value.setter
    def value(self, value: Data) -> None:
        self._manager.set_var(self._reference, value)

    @property
    def type(self) -> DataType:
        return self._manager.get_var_type(self._reference)

    @property
    def reference(self) -> Optional[str]:
        return self._reference


class Membrane(Data):
    def __init__(self, manager: MemoryManager, reference: str):
        self._manager = manager
        self._reference = reference

    @property
    def value(self) -> object:
        return self._manager.get_mem(self._reference)

    @value.setter
    def value(self, value: Data) -> None:
        self._manager.set_mem(self._reference, value)

    @property
    def type(self) -> DataType:
        return DataType.MULTISET

    @property
    def reference(self) -> Optional[str]:
        return self._reference


class MemoryManager:
    def __init__(self):
        self._level = 0
        self._memory: Dict[str, List[Tuple[int, DataType, object]]] = defaultdict(list)
        self._membranes: Dict[str, Multiset[str]] = defaultdict(Multiset[str])

    def level_up(self):
        self._level += 1

    def level_down(self):
        for ref, vars in self._memory.items():
            if len(vars) == 0:
                continue
            if vars[-1][0] == self._level:
                vars.pop()

    def get_var(self, ref: str) -> object:
        if len(self._memory[ref]):
            return self._memory[ref][-1][2]
        error('MemoryManager', 'NameError', f'{ref} is not defined')

    def set_var(self, ref: str, val: Data) -> None:
        item = (self._level, val.type, copy(val.value) if val.type == DataType.MULTISET else val.value)
        if len(self._memory[ref]) == 0 or self._memory[ref][-1][0] < self._level:
            self._memory[ref].append(item)
        self._memory[ref][-1] = item

    def get_var_type(self, ref: str) -> DataType:
        if len(self._memory[ref]):
            return self._memory[ref][-1][1]
        error('MemoryManager', 'NameError', f'{ref} is not defined')

    def get_mem(self, ref: str) -> Multiset:
        return self._membranes[ref]

    def set_mem(self, ref: str, val: Data) -> None:
        if val.type != DataType.MULTISET:
            error('MemoryManager', 'TypeError', f'Trying to set membrane value as a non multiset object')
        self._membranes[ref] = copy(val.value)

    def print_state(self):
        for ref, vals in self._memory.items():
            if len(vals):
                print(f'Var {ref} = {vals[-1][2]} of type {vals[-1][1]}')
        for ref, s in self._membranes.items():
            print(f'Membrane {ref} = {s}')
