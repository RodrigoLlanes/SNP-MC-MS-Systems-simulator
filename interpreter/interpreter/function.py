from abc import ABC, abstractmethod
from interpreter.errormanager import error
from typing import Optional, Callable, List

from interpreter.interpreter.memorymanager import DataType, Data


class Function(ABC):
    @abstractmethod
    def call(self, *args, **kwargs) -> Optional[Data]:
        pass


class BuiltinFunction(Function):
    def __init__(self, f: Callable) -> None:
        self.f = f

    def call(self, *args: Data, **kwargs: Data) -> Data:
        return self.f(*args, **kwargs)
