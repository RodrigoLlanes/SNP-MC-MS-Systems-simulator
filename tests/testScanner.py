import unittest

from interpreter.scanner import Scanner


class TestScanner(unittest.TestCase):
    def test(self):
        """
        Test
        """
        src = '''
            a = 12
            b = '12'; d = abz12s
            c = 'a a a'
            
            [2] ('a' 'b'+)* / {'a', 'b'} -> {'a'} <1>, {'b'} <2>
        '''
        for token in Scanner(src).scan():
            print(token)
