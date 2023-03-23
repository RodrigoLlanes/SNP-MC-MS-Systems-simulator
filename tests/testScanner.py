import unittest

from interpreter.scanner import Scanner


class TestScanner(unittest.TestCase):
    def test(self):
        """
        Test
        """
        src = '''
            in [0]
            out[4]
            
            [0] = {'a'} * 100
            
            <0> [0] --> [1]
            <1> [1] --> [2]
            <2> [1] --> [3]
            <0> [2] --> [4]
            <0> [3] --> [4]
            
            [0] 'a'+ / {'a'} --> {'a', 'b', 'c'} <0>
            
            [1] 'b'('a' 'a' 'a')+ / {'b'} --> {'a'} <1>
            [1] 'c'('a' 'a' 'a' 'a' 'a')+ / {'c'} --> {'a'} <2>
            
            [2] 'a' / {'a'} --> {'fizz'} <0>
            [3] 'a' / {'a'} --> {'buzz'} <0>
        '''
        for token in Scanner(src).scan():
            print(token)
