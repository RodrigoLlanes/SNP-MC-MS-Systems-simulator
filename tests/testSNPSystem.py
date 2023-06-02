import unittest
from typing import List

from automatons import DFA
from simulator.snpsystem import SNPSystem
from utils import Multiset


class TestSNPSystem(unittest.TestCase):
    def test(self) -> None:
        snp = SNPSystem[int, int]()

        snp.set_input(0)

        snp.add_symbols(1, *['1']*3)
        snp.add_symbols(2, *['1']*2)

        snp.add_channel(1, 5, 1)
        snp.add_channel(2, 0, 2)
        snp.add_channel(2, 5, 2)
        snp.add_channel(3, 5, 3)
        snp.add_channel(4, 5, 4)
        snp.add_channel(5, 2, 5)

        snp.add_rule(0, 'a', Multiset(['a']), {2: Multiset(['a'])})

        snp.add_rule(2, '1*a', Multiset(['1']), {5: Multiset(['1'])})
        snp.add_rule(2, '1*a', Multiset(['a']), {5: Multiset(['a'])})

        snp.add_rule(5, '1*a', Multiset(['1']), {2: Multiset(['1']), 1: Multiset(['1'])})
        snp.add_rule(5, '1*a', Multiset(['a']), {3: Multiset(['a'])})
        snp.add_rule(5, '1*a', Multiset(['a']), {4: Multiset(['a'])})

        result = snp.run(['a'], render_steps=True)

        print(result)
