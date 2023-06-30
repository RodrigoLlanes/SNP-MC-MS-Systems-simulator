import unittest
from math import log2

from interpreter.ast import Visitor, Binary, Unary, Literal, Grouping, Identifier, Struct, Function, Call, Sinapsis, \
    Production, T, Regex
from interpreter.scanner import Scanner
from interpreter.parser import Parser
from interpreter.token import TokenType


class Printer(Visitor[str]):
    def visitRegexExpr(self, expr: Regex) -> T:
        return f'R({",".join(e.accept(self) for e in expr.content)})'

    def visitProductionExpr(self, expr: Production) -> T:
        return f'R({expr.membrane.accept(self)},{expr.regex.accept(self) if expr.regex else None},{expr.consumed.accept(self)},P({", ".join(send.accept(self) + " " + channel.accept(self) for send, channel in expr.channels)}))'

    def visitSinapsisExpr(self, expr: Sinapsis) -> str:
        return 'S(' + expr.channel.accept(self) + ',' + expr.left.accept(self) + ',' + expr.right.accept(self) + ')'

    def visitCallExpr(self, expr: Call) -> str:
        return 'C(' + expr.identifier.accept(self) + ',A(' + ', '.join(map(lambda x: x.accept(self), expr.params)) + '))'

    def visitBinaryExpr(self, expr: Binary) -> str:
        return expr.operator.lexeme + '(' + expr.left.accept(self) + ',' + expr.right.accept(self) + ')'

    def visitFunctionExpr(self, expr: Function) -> str:
        return f'F{expr.identifier.lexeme}(A({" ".join(p.accept(self) for p in expr.parameters)})' +',I(' \
               + ';'.join(i.accept(self) for i in expr.instructions) + '))'

    def visitStructExpr(self, expr: Struct) -> str:
        return f'M({",".join(e.accept(self) for e in expr.content)})'

    def visitIdentifierExpr(self, expr: Identifier) -> str:
        return f'{expr.identifier.lexeme}'

    def visitGroupingExpr(self, expr: Grouping) -> str:
        return '(' + expr.expression.accept(self) + ')'

    def visitLiteralExpr(self, expr: Literal) -> str:
        if isinstance(expr.value, int):
            return f'N({str(expr.value)})'
        else:
            return f'T({str(expr.value)})'

    def visitUnaryExpr(self, expr: Unary) -> str:
        if expr.operator.token_type == TokenType.OPEN_MEMBRANE:
            return f'[{expr.right.accept(self)}]'
        if expr.operator.token_type == TokenType.OPEN_CHANNEL:
            return f'<{expr.right.accept(self)}>'
        return expr.operator.lexeme + '(' + expr.right.accept(self) + ')'


class TestParser(unittest.TestCase):
    def _test_parse(self, src: str, result: str) -> None:
        """
        Test if the parser parses a given source code
        """
        tokens = Scanner(src).scan()
        parsed = Parser(tokens).parse()
        parsed = parsed.accept(Printer())
        self.assertEqual(parsed, result)

    def print_parse(self, src, *args):
        tokens = Scanner(src).scan()
        parsed = Parser(tokens).parse()
        parsed = parsed.accept(Printer())
        print(f'self._test_parse("{src}",\n                "{parsed}")')


    def test_multiset(self):
        """
        Test the multiset definition
        """
        self._test_parse("{'1'}",
                         "Fmain(A(),I(M(T(1))))")
        self._test_parse("{'a', 'b', 'b'}",
                         "Fmain(A(),I(M(T(a),T(b),T(b))))")

    def test_operands(self):
        """
        Test the operators
        """
        self._test_parse("1 / 2",
                         "Fmain(A(),I(/(N(1),N(2))))")
        self._test_parse("4 * 8",
                         "Fmain(A(),I(*(N(4),N(8))))")
        self._test_parse("5 + (6 - 2)",
                         "Fmain(A(),I(+(N(5),(-(N(6),N(2))))))")
        self._test_parse("{'a'} & {'b'}",
                         "Fmain(A(),I(&(M(T(a)),M(T(b)))))")
        self._test_parse("{'a'} | {'b'}",
                         "Fmain(A(),I(|(M(T(a)),M(T(b)))))")
        self._test_parse("{'a'} + {'b'}",
                         "Fmain(A(),I(+(M(T(a)),M(T(b)))))")
        self._test_parse("{'a'} - {'b'}",
                         "Fmain(A(),I(-(M(T(a)),M(T(b)))))")

    def test_membranes_and_vars(self):
        """
        Test the membrane and vars declaration
        """
        self._test_parse("a = 12",
                         "Fmain(A(),I(=(a,N(12))))")
        self._test_parse("[1] = {'1'}",
                         "Fmain(A(),I(=([N(1)],M(T(1)))))")

    def test_productions(self):
        """
        Test the productions definition
        """
        self._test_parse("[0] 'a' / {'a'} --> {'a'} <2>",
                         "Fmain(A(),I(R([N(0)],R(T(a)),M(T(a)),P(M(T(a)) <N(2)>))))")
        self._test_parse("[0] 'a'+ / {'b'} --> {'a'} <2>",
                         "Fmain(A(),I(R([N(0)],R(+(T(a))),M(T(b)),P(M(T(a)) <N(2)>))))")
        self._test_parse("[0] {'b'} --> {'a'} <2> : 3",
                         "Fmain(A(),I(R([N(0)],None,M(T(b)),P(M(T(a)) <N(2)>))))")
        self._test_parse("[0] ('a'+'b')*/{'a'}-->{'a'}<2>,{'b'}<1>:1",
                         "Fmain(A(),I(R([N(0)],R(*((R(+(T(a)),T(b))))),M(T(a)),P(M(T(a)) <N(2)>, M(T(b)) <N(1)>))))")

    def test_sinapsis(self):
        """
        Test the sinapsis definition
        """
        self._test_parse("<1> [ 0] --> [1 ]",
                         "Fmain(A(),I(S(<N(1)>,[N(0)],[N(1)])))")
        self._test_parse("<2 > [1] --> out",
                         "Fmain(A(),I(S(<N(2)>,[N(1)],out)))")
        self._test_parse("< 0 >  [ 0 ] -->   out ",
                         "Fmain(A(),I(S(<N(0)>,[N(0)],out)))")

    def test_functions(self):
        """
        Test the functions
        """
        self._test_parse("input([1])",
                         "Fmain(A(),I(C(input,A([N(1)]))))")
        self._test_parse("f('a', [1])",
                         "Fmain(A(),I(C(f,A(T(a), [N(1)]))))")
        self._test_parse("input(1, '1')",
                         "Fmain(A(),I(C(input,A(N(1), T(1)))))")
