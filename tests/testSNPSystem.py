import unittest
from typing import List

from automatons import DFA
from simulator.snpsystem import SNPSystem
from utils import Multiset


class TestSNPSystem(unittest.TestCase):
    def test(self) -> None:
        snp = SNPSystem[int, int]()
        snp.set_input(0)
        snp.set_output(1)
        snp.add_rule()
