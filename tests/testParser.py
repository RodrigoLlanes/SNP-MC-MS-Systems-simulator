import unittest

from interpreter.ast import Visitor, Binary, T, Unary, Literal, Grouping, Variable, Struct, Function
from interpreter.scanner import Scanner
from interpreter.parser import Parser
from interpreter.token import TokenType


class Printer(Visitor[str]):
    def visitFunctionExpr(self, expr: Function) -> T:
        return f'def {expr.identifier.lexeme} ({", ".join(p.accept(self) for p in expr.parameters)})' + '{\n    ' \
               + '\n    '.join(i.accept(self) for i in expr.instructions) + '\n}'

    def visitStructExpr(self, expr: Struct) -> T:
        return f'[{" ".join(e.accept(self) for e in expr.content)}]{expr.identifier.lexeme}'

    def visitVariableExpr(self, expr: Variable) -> T:
        return f'{expr.variable.lexeme}'

    def visitGroupingExpr(self, expr: Grouping) -> T:
        return '(' + expr.expression.accept(self) + ')'

    def visitLiteralExpr(self, expr: Literal) -> T:
        return str(expr.value)

    def visitUnaryExpr(self, expr: Unary) -> T:
        return expr.operator.lexeme + ' ' + expr.right.accept(self)

    def visitBinaryExpr(self, expr: Binary) -> T:
        if expr.operator.token_type == TokenType.
        return expr.left.accept(self) + ' ' + expr.operator.lexeme + ' ' + expr.right.accept(self)


class TestParser(unittest.TestCase):
    def test(self):
        """
        Test
        """
        src = """
        @a(12+3) = 17;
        1 + (a*2-1) % 5;
        $z = @b(11);
        [[]'2 [[]'4]'3]'1;
        """
        tokens = Scanner(src).scan()
        parsed = Parser(tokens).parse()
        print(parsed.accept(Printer()))
