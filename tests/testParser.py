import unittest
from typing import List

from interpreter.ast import Visitor, Binary, T, Unary, Literal, Grouping, Variable
from interpreter.scanner import Scanner
from interpreter.parser import Parser


class Printer(Visitor[str]):
    def visitVariableExpr(self, expr: Variable) -> T:
        return f'({expr.variable.lexeme})'

    def visitGroupingExpr(self, expr: Grouping) -> T:
        return '(' + expr.expression.accept(self) + ')'

    def visitLiteralExpr(self, expr: Literal) -> T:
        return str(expr.value)

    def visitUnaryExpr(self, expr: Unary) -> T:
        return '(' + expr.operator.lexeme + ' ' + expr.right.accept(self) + ')'

    def visitBinaryExpr(self, expr: Binary) -> T:
        return '(' + expr.left.accept(self) + ' ' + expr.operator.lexeme + ' ' + expr.right.accept(self) + ')'


class TestParser(unittest.TestCase):
    def test(self):
        """
        Test
        """
        src = """
        @a(12+3) = 17;
        1 + (a*2-1) % 5;
        z = @(11);
        """
        tokens = Scanner(src).scan()
        parsed = Parser(tokens).parse()
        for line in parsed:
            print(line.accept(Printer()))
