import unittest

from interpreter.ast import Visitor, Binary, Unary, Literal, Grouping, Identifier, Struct, Function, Call, Sinapsis, \
    Production, T, Regex
from interpreter.scanner import Scanner
from interpreter.parser import Parser


class Printer(Visitor[str]):
    def visitRegexExpr(self, expr: Regex) -> T:
        return f'{" ".join(e.accept(self) for e in expr.content)}'

    def visitProductionExpr(self, expr: Production) -> T:
        return f'{expr.membrane.accept(self)} {expr.regex.accept(self)} / {expr.consumed.accept(self)} --> {", ".join(send.accept(self) + " " + channel.accept(self) for send, channel in expr.channels)}'

    def visitSinapsisExpr(self, expr: Sinapsis) -> str:
        return expr.channel.accept(self) + ' ' + expr.left.accept(self) + ' -->' + expr.right.accept(self)

    def visitCallExpr(self, expr: Call) -> str:
        return expr.identifier.accept(self) + '(' + ', '.join(map(lambda x: x.accept(self), expr.params)) + ')'

    def visitBinaryExpr(self, expr: Binary) -> str:
        return expr.left.accept(self) + ' ' + expr.operator.lexeme + ' ' + expr.right.accept(self)

    def visitFunctionExpr(self, expr: Function) -> str:
        return f'def {expr.identifier.lexeme} ({", ".join(p.accept(self) for p in expr.parameters)})' + '{\n    ' \
               + '\n    '.join(i.accept(self) for i in expr.instructions) + '\n}'

    def visitStructExpr(self, expr: Struct) -> str:
        return f'[{" ".join(e.accept(self) for e in expr.content)}]'

    def visitIdentifierExpr(self, expr: Identifier) -> str:
        return f'{expr.identifier.lexeme}'

    def visitGroupingExpr(self, expr: Grouping) -> str:
        return '(' + expr.expression.accept(self) + ')'

    def visitLiteralExpr(self, expr: Literal) -> str:
        return str(expr.value)

    def visitUnaryExpr(self, expr: Unary) -> str:
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
            
            <1+2> [2+3] --> [0]
            [0] ('a' 'a' 'b'*)+ / {'a', 'b'} --> {'a', 'a'} <0>, {'b'} <1>
        """
        tokens = Scanner(src).scan()
        parsed = Parser(tokens).parse()
        print(parsed.accept(Printer()))
