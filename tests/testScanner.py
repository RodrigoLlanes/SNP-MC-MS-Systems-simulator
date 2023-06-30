import unittest
from typing import List

from interpreter.scanner import Scanner
from interpreter.token import TokenType


class TestScanner(unittest.TestCase):
    def _test_scan(self, src: str, lexemes: List[str], types: List[TokenType]) -> None:
        """
        Test if the scanner identifies the lexemes and token types of a given source code
        """
        scanned = Scanner(src).scan()
        self.assertListEqual([t.lexeme for t in scanned], lexemes)
        self.assertListEqual([t.token_type for t in scanned], types)

    def test_multiset(self):
        """
        Test the multiset definition
        """
        self._test_scan("{'1'}",
                        ['{', "'1'", '}', '*', '3', 'EOF'],
                        [TokenType.OPEN_SET, TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.MULT, TokenType.NUMBER,
                         TokenType.EOF])

        self._test_scan("{'a', 'b', 'b'}",
                        ['{', "'a'", ',', "'b'", ',', "'b'", '}', '+', '{', "'a'", '}', 'EOF'],
                        [TokenType.OPEN_SET, TokenType.SYMBOL, TokenType.COMMA, TokenType.SYMBOL, TokenType.COMMA,
                         TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.PLUS, TokenType.OPEN_SET, TokenType.SYMBOL,
                         TokenType.CLOSE_SET, TokenType.EOF])

    def test_operands(self):
        """
        Test the operators
        """
        self._test_scan("1 / 2",
                        ['1', '/', '2', 'EOF'],
                        [TokenType.NUMBER, TokenType.DIV, TokenType.NUMBER, TokenType.EOF])
        self._test_scan("4 * 8",
                        ['4', '*', '8', 'EOF'],
                        [TokenType.NUMBER, TokenType.MULT, TokenType.NUMBER, TokenType.EOF])
        self._test_scan("5 + (6 - 2)",
                        ['5', '+', '(', '6', '-', '2', ')', 'EOF'],
                        [TokenType.NUMBER, TokenType.PLUS, TokenType.OPEN_PAREN, TokenType.NUMBER, TokenType.MINUS,
                         TokenType.NUMBER, TokenType.CLOSE_PAREN, TokenType.EOF])
        self._test_scan("{'a'} & {'b'}",
                        ['{', "'a'", '}', '&', '{', "'b'", '}', 'EOF'],
                        [TokenType.OPEN_SET, TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.INTERSECTION,
                         TokenType.OPEN_SET, TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.EOF])
        self._test_scan("{'a'} | {'b'}",
                        ['{', "'a'", '}', '|', '{', "'b'", '}', 'EOF'],
                        [TokenType.OPEN_SET, TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.UNION, TokenType.OPEN_SET,
                         TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.EOF])
        self._test_scan("{'a'} + {'b'}",
                        ['{', "'a'", '}', '+', '{', "'b'", '}', 'EOF'],
                        [TokenType.OPEN_SET, TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.PLUS, TokenType.OPEN_SET,
                         TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.EOF])
        self._test_scan("{'a'} - {'b'}",
                        ['{', "'a'", '}', '-', '{', "'b'", '}', 'EOF'],
                        [TokenType.OPEN_SET, TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.MINUS, TokenType.OPEN_SET,
                         TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.EOF])

    def test_membranes_and_vars(self):
        """
        Test the membrane and vars declaration
        """
        self._test_scan("a = 12",
                        ['a', '=', '12', 'EOF'],
                        [TokenType.IDENTIFIER, TokenType.EQUAL, TokenType.NUMBER, TokenType.EOF])
        self._test_scan("[1] = {'1'}",
                        ['[', '1', ']', '=', '{', "'1'", '}', 'EOF'],
                        [TokenType.OPEN_MEMBRANE, TokenType.NUMBER, TokenType.CLOSE_MEMBRANE, TokenType.EQUAL,
                         TokenType.OPEN_SET, TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.EOF])

    def test_productions(self):
        """
        Test the productions definition
        """
        self._test_scan("[0] 'a' / {'a'} --> {'a'} <2>",
                        ['[', '0', ']', "'a'", '/', '{', "'a'", '}', '-->', '{', "'a'", '}', '<', '2', '>', 'EOF'],
                        [TokenType.OPEN_MEMBRANE, TokenType.NUMBER, TokenType.CLOSE_MEMBRANE, TokenType.SYMBOL,
                         TokenType.DIV, TokenType.OPEN_SET, TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.THEN,
                         TokenType.OPEN_SET, TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.OPEN_CHANNEL,
                         TokenType.NUMBER, TokenType.CLOSE_CHANNEL, TokenType.EOF])
        self._test_scan("[0] 'a'+ / {'b'} --> {'a'} <2>",
                        ['[', '0', ']', "'a'", '+', '/', '{', "'b'", '}', '-->', '{', "'a'", '}', '<', '2', '>', 'EOF'],
                        [TokenType.OPEN_MEMBRANE, TokenType.NUMBER, TokenType.CLOSE_MEMBRANE, TokenType.SYMBOL,
                         TokenType.PLUS, TokenType.DIV, TokenType.OPEN_SET, TokenType.SYMBOL, TokenType.CLOSE_SET,
                         TokenType.THEN, TokenType.OPEN_SET, TokenType.SYMBOL, TokenType.CLOSE_SET,
                         TokenType.OPEN_CHANNEL, TokenType.NUMBER, TokenType.CLOSE_CHANNEL, TokenType.EOF])
        self._test_scan("[0] {'b'} --> {'a'} <2> : 3",
                        ['[', '0', ']', '{', "'b'", '}', '-->', '{', "'a'", '}', '<', '2', '>', ':', '3', 'EOF'],
                        [TokenType.OPEN_MEMBRANE, TokenType.NUMBER, TokenType.CLOSE_MEMBRANE, TokenType.OPEN_SET,
                         TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.THEN, TokenType.OPEN_SET, TokenType.SYMBOL,
                         TokenType.CLOSE_SET, TokenType.OPEN_CHANNEL, TokenType.NUMBER, TokenType.CLOSE_CHANNEL,
                         TokenType.COLON, TokenType.NUMBER, TokenType.EOF])
        self._test_scan("[0] ('a'+'b')*/{'a'}-->{'a'}<2>,{'b'}<1>:1",
                        ['[', '0', ']', '(', "'a'", '+', "'b'", ')', '*', '/','{', "'a'", '}', '-->', '{', "'a'", '}', '<',
                         '2', '>', ',', '{', "'b'", '}', '<', '1', '>', ':', '1', 'EOF'],
                        [TokenType.OPEN_MEMBRANE, TokenType.NUMBER, TokenType.CLOSE_MEMBRANE, TokenType.OPEN_PAREN,
                         TokenType.SYMBOL, TokenType.PLUS, TokenType.SYMBOL, TokenType.CLOSE_PAREN, TokenType.MULT,
                         TokenType.DIV, TokenType.OPEN_SET, TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.THEN,
                         TokenType.OPEN_SET, TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.OPEN_CHANNEL,
                         TokenType.NUMBER, TokenType.CLOSE_CHANNEL, TokenType.COMMA, TokenType.OPEN_SET,
                         TokenType.SYMBOL, TokenType.CLOSE_SET, TokenType.OPEN_CHANNEL, TokenType.NUMBER,
                         TokenType.CLOSE_CHANNEL, TokenType.COLON, TokenType.NUMBER, TokenType.EOF])

    def test_sinapsis(self):
        """
        Test the sinapsis definition
        """
        self._test_scan("<1> [ 0] --> [1 ]",
                        ['<', '1', '>', '[', '0', ']', '-->', '[', '1', ']', 'EOF'],
                        [TokenType.OPEN_CHANNEL, TokenType.NUMBER, TokenType.CLOSE_CHANNEL, TokenType.OPEN_MEMBRANE,
                         TokenType.NUMBER, TokenType.CLOSE_MEMBRANE, TokenType.THEN, TokenType.OPEN_MEMBRANE,
                         TokenType.NUMBER, TokenType.CLOSE_MEMBRANE, TokenType.EOF])
        self._test_scan("<2 > [1] --> out",
                        ['<', '2', '>', '[', '1', ']', '-->', 'out', 'EOF'],
                        [TokenType.OPEN_CHANNEL, TokenType.NUMBER, TokenType.CLOSE_CHANNEL, TokenType.OPEN_MEMBRANE,
                         TokenType.NUMBER, TokenType.CLOSE_MEMBRANE, TokenType.THEN, TokenType.IDENTIFIER,
                         TokenType.EOF])
        self._test_scan("< 0 >  [ 0 ] -->   out ",
                        ['<', '0', '>', '[', '0', ']', '-->', 'out', 'EOF'],
                        [TokenType.OPEN_CHANNEL, TokenType.NUMBER, TokenType.CLOSE_CHANNEL, TokenType.OPEN_MEMBRANE,
                         TokenType.NUMBER, TokenType.CLOSE_MEMBRANE, TokenType.THEN, TokenType.IDENTIFIER,
                         TokenType.EOF])

    def test_functions(self):
        """
        Test the functions
        """
        self._test_scan("input([1])",
                        ['input', '(', '[', '1', ']', ')', 'EOF'],
                        [TokenType.IDENTIFIER, TokenType.OPEN_PAREN, TokenType.OPEN_MEMBRANE, TokenType.NUMBER,
                         TokenType.CLOSE_MEMBRANE, TokenType.CLOSE_PAREN, TokenType.EOF])
        self._test_scan("f('a', [1])",
                        ['f', '(', "'a'", ',', '[', '1', ']', ')', 'EOF'],
                        [TokenType.IDENTIFIER, TokenType.OPEN_PAREN, TokenType.SYMBOL, TokenType.COMMA,
                         TokenType.OPEN_MEMBRANE, TokenType.NUMBER, TokenType.CLOSE_MEMBRANE, TokenType.CLOSE_PAREN,
                         TokenType.EOF])
        self._test_scan("input(1, '1')",
                        ['input', '(', '1', ',', "'1'", ')', 'EOF'],
                        [TokenType.IDENTIFIER, TokenType.OPEN_PAREN, TokenType.NUMBER, TokenType.COMMA,
                         TokenType.SYMBOL, TokenType.CLOSE_PAREN, TokenType.EOF])
