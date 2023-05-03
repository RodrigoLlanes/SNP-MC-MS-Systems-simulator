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
            
            [0] += [1] + s2
            
            input([1])
            
            # Se cambia el tipo de symb
            symb = 12
            
            <1+2> [symb+3] --> [0]
            [0] ('a' 'a' 'b'*)+ / {'a', 'b'} --> {'a', 'a'} <0>, {'b'} <1>
            
            [1] 'symbol'+'a'+ / {'symbol', 'a'} --> {'a'} <3>
            <3> [1] --> [1]
            
            [1] = {'symbol', 'symbol', 'a'}
        """
        tokens = Scanner(src).scan()
        parsed = Parser(tokens).parse()
        model = Interpreter(parsed).run()
        model.run([], True, render_path='../tmp')
