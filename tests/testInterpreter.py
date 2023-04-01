import unittest

from interpreter.interpreter import Interpreter
from interpreter.scanner import Scanner
from interpreter.parser import Parser


class TestInterpreter(unittest.TestCase):
    def test(self):
        """
        Test
        """
        src = """
            symb = 'a' + 1
            [0] = {symb} * 100

            s1 = {'a1', 'b'} * (3*5/2)
            aux = s2 = {'a1'} & s1
            s3 = {symb} | s2
            s2 = s3 + s2
            
            [0] += s3
        """
        tokens = Scanner(src).scan()
        parsed = Parser(tokens).parse()
        print(parsed.accept(Interpreter(parsed)))
