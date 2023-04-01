from typing import List, Tuple

from interpreter.ast import Expr, Binary, Unary, Literal, Grouping, Identifier, Struct, Function
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

    def check(self, types: TokenType, d: int = 0) -> bool:
        if self.peek(d).token_type in types:
            return True
        return False

    def match(self, types: TokenType) -> bool:
        if self.check(types):
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

    def program(self) -> Function:
        statements = []
        while not self.at_end():
            statements.append(self.statement())
        return Function(Token(TokenType.IDENTIFIER, 'main', None, 0), [], statements)

    def statement(self) -> Expr:
        statement = self.expression()

        if statement is None:
            raise self.error(self.peek(), "Unexpected token.")
        if self.consume(TokenType.END, f"Semicolon or end of line expected"):
            return statement

    def identifier(self) -> Expr:
        if self.check(TokenType.IDENTIFIER):
            return Identifier(self.advance())
        if self.check(TokenType.OPEN_MEMBRANE):
            identifier = Unary(self.advance(), self.expression())
            self.consume(TokenType.CLOSE_MEMBRANE, 'Close membrane expected')
            return identifier
        if self.check(TokenType.OPEN_CHANNEL):
            identifier = Unary(self.advance(), self.expression())
            self.consume(TokenType.CLOSE_CHANNEL, 'Close chanel expected')
            return identifier
        self.error(self.peek(), 'Identifier expected')

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        checkpoint = self.current

        if self.check(TokenType.IDENTIFIER | TokenType.OPEN_MEMBRANE | TokenType.OPEN_CHANNEL):
            identifier = self.identifier()
            if self.check(TokenType.ASSIGNMENT):
                op = self.advance()
                return Binary(identifier, op, self.assignment())
        self.current = checkpoint
        return self.logical()

    def logical(self) -> Expr:
        expr = self.term()
        while self.match(TokenType.UNION | TokenType.INTERSECTION):
            op = self.peek(-1)
            right = self.term()
            expr = Binary(expr, op, right)
        return expr

    def term(self) -> Expr:
        expr = self.factor()
        while self.match(TokenType.MINUS | TokenType.PLUS):
            op = self.peek(-1)
            right = self.factor()
            expr = Binary(expr, op, right)
        return expr

    def factor(self) -> Expr:
        expr = self.unary()
        while self.match(TokenType.DIV | TokenType.MULT | TokenType.MOD):
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
            return Literal(int(self.peek(-1).literal))
        if self.match(TokenType.SYMBOL):
            return Literal(self.peek(-1).literal)

        if self.match(TokenType.OPEN_SET):
            if self.match(TokenType.CLOSE_SET):
                return Struct([])
            struct = [self.expression()]
            while self.match(TokenType.COMMA):
                struct.append(self.expression())
            self.consume(TokenType.CLOSE_SET, 'Expected closing set.')
            return Struct(struct)

        if self.check(TokenType.IDENTIFIER):
            return Identifier(self.advance())

        if self.match(TokenType.OPEN_PAREN):
            expr = self.expression()
            self.consume(TokenType.CLOSE_PAREN, 'Expected closing parenthesis.')
            return Grouping(expr)

        self.error(self.peek(), 'Expected expression.')
