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
        snp.add_channel(0, 0, 1)
        snp.add_channel(0, 1, 2)
        snp.add_rule(0, 'a+', Multiset(['a']), {0: Multiset(['a'])})
        snp.add_rule(1, ['(','a','a',')','+'], Multiset(['a']), {0: Multiset(['b','b'])})
        snp.add_rule(1, 'a+', Multiset(['a', 'a']), {0: Multiset(['c'])})
        snp.add_symbols(0, *['a']*10)

        result = snp.run(['a'], render_steps=True)

        print(result)
