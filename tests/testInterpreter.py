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
            <3> [1] --> [0]
            
            [1] = {'symbol', 'symbol', 'a'}
            <3> [1] --> out
        """
        src = """
            input([0])
            
            [1] = {'1'} * 3
            [2] = {'1'} * 2
            
            <1> [5] --> [1]
            <2> [0] --> [2]
            <2> [5] --> [2]
            <3> [5] --> [3]
            <4> [5] --> [4]
            <5> [2] --> [5]
            
            [0] {'a'} --> {'a'} <2>
            
            [2] {'1'} --> lambda
            [2] '1'* 'a' / {'a'} --> {'a'} <5>
            
            [5] '1'* 'a' / {'1'} --> {'1'} <2>, {'1'} <1>
            [5] '1'* 'a' / {'a'} --> {'a'} <3>
            [5] '1'* 'a' / {'a'} --> {'a'} <4>  
        """
        tokens = Scanner(src).scan()
        parsed = Parser(tokens).parse()
        model = Interpreter(parsed).run()
        model.run(['a'], True, render_path='../tmp')
