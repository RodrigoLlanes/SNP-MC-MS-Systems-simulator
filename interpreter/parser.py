from typing import List

from interpreter.ast import Expr, Binary, Unary, Literal, Grouping
from interpreter.token import Token, TokenType


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens: List[Token] = tokens
        self.current: int = 0

    def peek(self, d: int = 0):
        return self.tokens[self.current + d]

    def at_end(self):
        return self.peek().token_type == TokenType.EOF

    def advance(self):
        if not self.at_end():
            self.current += 1
        return self.peek(-1)

    def check(self, token_type: TokenType) -> bool:
        if self.at_end():
            return False
        return self.peek().token_type == token_type

    def match(self, *types: TokenType) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def error(self, token: Token, message: str) -> Exception:
        if token.token_type == TokenType.EOF:
            return Exception(f'Error at end of file (line {token.line}): {message}')
        else:
            return Exception(f'Error at "{token.lexeme}" (line {token.line}): {message}')

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        raise self.error(self.peek(), message)

    def expression(self) -> Expr:
        return self.term()

    def term(self) -> Expr:
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            op = self.peek(-1)
            right = self.factor()
            expr = Binary(expr, op, right)
        return expr

    def factor(self) -> Expr:
        expr = self.unary()
        while self.match(TokenType.DIV, TokenType.MULT, TokenType.MOD):
            op = self.peek(-1)
            right = self.unary()
            expr = Binary(expr, op, right)
        return expr

    def unary(self) -> Expr:
        if self.match(TokenType.MINUS):
            op = self.peek(-1)
            right = self.unary()
            return Unary(op, right)
        return self.primary()

    def primary(self) -> Expr:
        if self.match(TokenType.NUMBER, TokenType.SYMBOL):
            return Literal(self.peek(-1).literal)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, 'Expected closing parenthesis.')
            return Grouping(expr)

        self.error(self.peek(), 'Expected expression.')

    def parse(self) -> Expr:
        return self.expression()
