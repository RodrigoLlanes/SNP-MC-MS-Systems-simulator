from typing import List, Tuple

from interpreter.ast import Expr, Binary, Unary, Literal, Grouping, Variable
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

    def check(self, *types: TokenType, d: int = 0) -> bool:
        for t in types:
            if self.peek(d).token_type == t:
                return True
        return False

    def match(self, *types: TokenType) -> bool:
        if self.check(*types):
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

    def parse(self) -> List[Expr]:
        return self.program()

    def program(self) -> List[Expr]:
        statements = []
        while not self.at_end():
            statement = self.statement()
            if statement is not None:
                statements.append(statement)
            else:
                raise self.error(self.peek(), "Unexpected token.")
        return statements

    def statement(self) -> Expr:
        statement = self.assignment()
        if self.consume(TokenType.SEMICOLON, f"Semicolon expected"):
            return statement

    def identifier(self) -> Expr:
        if self.check(TokenType.IDENTIFIER):
            return Variable(self.advance())

        if self.check(TokenType.PROPERTY):
            prop = Variable(self.advance())
            if self.check(TokenType.LEFT_PAREN):
                open_paren = self.advance()
                index = self.expression()
                self.consume(TokenType.RIGHT_PAREN, "Expected right parenthesis")
                return Binary(prop, open_paren, index)
            else:
                return prop

        raise self.error(self.peek(), 'Identifier expected')

    def assignment(self) -> Expr:
        if self.check(TokenType.PROPERTY, TokenType.IDENTIFIER):
            checkpoint = self.current
            identifier = self.identifier()
            if self.check(TokenType.EQUAL, TokenType.PLUS_EQUAL):
                op = self.advance()
                return Binary(identifier, op, self.expression())
            self.current = checkpoint
        return self.expression()

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
        if self.match(TokenType.NUMBER):
            return Literal(self.peek(-1).literal)

        if self.check(TokenType.IDENTIFIER, TokenType.PROPERTY):
            return self.identifier()

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, 'Expected closing parenthesis.')
            return Grouping(expr)

        self.error(self.peek(), 'Expected expression.')
