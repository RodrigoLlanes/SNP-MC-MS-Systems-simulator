import unittest

from interpreter.ast import Visitor, Binary, T, Unary, Literal, Grouping, Identifier, Struct, Function
from interpreter.scanner import Scanner
from interpreter.parser import Parser
from interpreter.token import TokenType


class Printer(Visitor[str]):
    def visitBinaryExpr(self, expr: Binary) -> T:
        return expr.left.accept(self) + ' ' + expr.operator.lexeme + ' ' + expr.right.accept(self)

    def visitFunctionExpr(self, expr: Function) -> T:
        return f'def {expr.identifier.lexeme} ({", ".join(p.accept(self) for p in expr.parameters)})' + '{\n    ' \
               + '\n    '.join(i.accept(self) for i in expr.instructions) + '\n}'

    def visitStructExpr(self, expr: Struct) -> T:
        return f'[{" ".join(e.accept(self) for e in expr.content)}]'

    def visitVariableExpr(self, expr: Identifier) -> T:
        return f'{expr.identifier.lexeme}'

    def visitGroupingExpr(self, expr: Grouping) -> T:
        return '(' + expr.expression.accept(self) + ')'

    def visitLiteralExpr(self, expr: Literal) -> T:
        return str(expr.value)

    def visitUnaryExpr(self, expr: Unary) -> T:
        return expr.operator.lexeme + ' ' + expr.right.accept(self)


class TestParser(unittest.TestCase):
    def test(self):
        """
        Test
        """
        src = """
            symb = 'a' + 1
            [0] = {symb} * 100
            
            s1 = {'a', 'b'} * (3*5/2)
            s2 = {'a'} & s1
            s3 = {'a'} | s2
        """
        tokens = Scanner(src).scan()
        parsed = Parser(tokens).parse()
        print(parsed.accept(Printer()))
