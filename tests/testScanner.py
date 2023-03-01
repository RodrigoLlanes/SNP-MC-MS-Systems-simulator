import unittest

from interpreter.scanner import Scanner


class TestScanner(unittest.TestCase):
    def test(self):
        """
        Test
        """
        src = '''
        def main()
        {
            @mu = [[[]'3 []'4]'2]'1;
            @ms(3) = a,f;
            
            [a --> a,bp]'3;
            [a --> bp,@d]'3;
            [f --> f*2]'3;
            
            [bp --> b]'2;
            [b []'4 --> b [c]'4]'2;
            (1) [f*2 --> f ]'2;
            (2) [f --> a,@d]'2;
        }
        '''
        for token in Scanner(src).scan():
            print(token)
