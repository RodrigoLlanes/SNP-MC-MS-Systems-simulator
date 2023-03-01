import unittest
from typing import List

from automatons import DFA
from utils import Multiset


class TestDFA(unittest.TestCase):
    def _test_accepts(self, regex: str, accepts: List[str], rejects: List[str], multiset: bool = False) -> None:
        """
        Test if an automaton described by the regular expression regex accepts and rejects the specified words
        """
        automaton = DFA.from_RegEx(regex)
        if multiset:
            for positive in accepts:
                self.assertTrue(automaton.accepts_multiset(Multiset(positive)))
            for negative in rejects:
                self.assertFalse(automaton.accepts_multiset(Multiset(negative)))
        else:
            for positive in accepts:
                self.assertTrue(automaton.accepts(positive))
            for negative in rejects:
                self.assertFalse(automaton.accepts(negative))

    def test_word_acceptation(self):
        """
        Test the automaton word acceptation and rejection
        """
        self._test_accepts('a*b*', ['', 'b', 'ab', 'aab'], ['c', 'ba', 'bba', 'abc'])
        self._test_accepts('(ab)+c*', ['ab', 'abc', 'ababccc'], ['', 'c', 'cab', 'acc'])

    def test_multiset_acceptation(self):
        """
        Test the automaton multiset acceptation and rejection
        """
        self._test_accepts('a*b*', ['', 'b', 'ba', 'ab', 'aab', 'bba'], ['c', 'abc'], multiset=True)
        self._test_accepts('(ab)+c*', ['ab', 'cab', 'abc', 'ababccc'], ['', 'c', 'acc'], multiset=True)
