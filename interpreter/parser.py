from typing import List, Tuple

from interpreter.ast import Expr, Binary, Unary, Literal, Grouping, Variable, Struct, Function
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

    def parse(self) -> Function:
        return self.program()

    def consume_empty(self):
        while self.match(TokenType.END):
            pass

    def program(self) -> Function:
        statements = []
        while not self.at_end():
            self.consume_empty()
            statement = self.statement()
            if statement is not None:
                statements.append(statement)
            else:
                raise self.error(self.peek(), "Unexpected token.")
        return Function(Token(TokenType.IDENTIFIER, 'main', None, 0), [], statements)

    def statement(self) -> Expr:
        statement = self.assignment()
        if self.consume(TokenType.END, f"Semicolon or end of line expected"):
            return statement

    def identifier(self) -> Expr:
        return Variable(self.advance())

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
        if self.match(TokenType.NUMBER, TokenType.SYMBOL):
            return Literal(self.peek(-1).literal)

        if self.check(TokenType.IDENTIFIER, TokenType.PROPERTY):
            return self.identifier()

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, 'Expected closing parenthesis.')
            return Grouping(expr)

        if self.match(TokenType.LEFT_BRACKET):
            content = []
            while self.check(TokenType.LEFT_BRACKET):
                content.append(self.expression())
            self.consume(TokenType.RIGHT_BRACKET, 'Expected closing bracket.')
            identifier = self.consume(TokenType.LABEL, 'Expected label.')
            return Struct(identifier, content)

        self.error(self.peek(), 'Expected expression.')
