import unittest
from typing import Dict, List, Union, Optional

from interpreter.interpreter import Interpreter
from interpreter.scanner import Scanner
from interpreter.parser import Parser
from simulator.snpsystem import SNPSystem
from utils import Multiset


class TestInterpreter(unittest.TestCase):
    def _test_output(self, src: str, mode: str, output: Union[Multiset[str], Dict[str, Multiset[str]],
                                                              List[Multiset[str]], List[Dict[str, Multiset[str]]]],
                     input_data: Optional[Multiset[str]] = None):
        """
        Test if the interpreter generated model returns the expected output
        """
        tokens = Scanner(src).scan()
        parsed = Parser(tokens).parse()
        model = Interpreter(parsed).run()
        res = model.run(input_data if input_data else Multiset(), mode=mode)
        match mode:
            case 'halt':
                self.assertEqual(res, output)
            case 'halt-ch':
                self.assertDictEqual(res, output)
            case 'time':
                self.assertListEqual(res, output)
            case 'time-ch':
                self.assertEqual(len(res), len(output))
                for a, b in zip(res, output):
                    self.assertDictEqual(a, b)

    def test_interpreter(self):
        """
        Test some source codes
        """
        src = '''
        input([0])
        
        <1> [0] --> out
        <2> [0] --> [2]
        
        [0] {'a'} --> {'1'} <1>, {'a'} <2>
        '''
        self._test_output(src, 'halt', Multiset(['1']), Multiset(['a']))

        src = '''
        input([0])

        <0> [1] --> [0]
        <1> [0] --> [1]
        <2> [1] --> out
        <2> [0] --> out

        [0] 'a' 'a'+ / {'a'} --> {'a'} <1>
        [0] {'a'} --> {'1'} <2>
        
        [1] 'a' 'a'+ / {'a'} --> {'a'} <0>
        [1] {'a'} --> {'1'} <2>
        '''
        self._test_output(src, 'halt', Multiset(['1']*10), Multiset(['a']*10))

        src = '''
        input([0])

        [2] = {'1'} * 2

        <1> [5] --> out
        <2> [0] --> [2]
        <2> [5] --> [2]
        <3> [5] --> [3]
        <4> [5] --> [4]
        <5> [2] --> [5]

        [0] 'a' / {'a'} --> {'a'} <2>

        [2] '1'* 'a' / {'1'} --> {'1'} <5>
        [2] {'a'} --> {'a'} <5>

        [5] '1'* 'a' / {'1'} --> {'1'} <2>, {'1'} <1>
        [5] {'a'} --> {'a'} <3>
        [5] {'a'} --> {'a'} <4>
        '''
        self._test_output(src, 'halt', Multiset(['1'] * 2), Multiset(['a']))
