from typing import List, Tuple, Optional

from interpreter.ast import Expr, Binary, Unary, Literal, Grouping, Identifier, Struct, Function, Call, Sinapsis, Regex, \
    Production
from interpreter.errormanager import error
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

    def error(self, token: Token, message: str) -> None:
        if token.token_type == TokenType.EOF:
            error('Parser', 'SyntaxError', f'{message} at end of file (line {token.line})')
        else:
            error('Parser', 'SyntaxError', f'{message} at "{token.lexeme}" (line {token.line})')

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        self.error(self.peek(), message)

    def parse(self) -> Function:
        return self.program()

    def program(self) -> Function:
        statements = []
        while not self.at_end():
            statements.append(self.statement())
        return Function(Token(TokenType.IDENTIFIER, 'main', None, 0), [], statements)

    def statement(self) -> Expr:
        # Non value expressions
        if self.check(TokenType.OPEN_CHANNEL):
            statement = self.sinapsis()
        elif prod := self.production():
            statement = prod
        else:
            statement = self.expression()

        if statement is None:
            self.error(self.peek(), "Unexpected token.")
        if self.at_end() or self.consume(TokenType.END, f"Semicolon or end of line expected"):
            return statement

    def function_call(self) -> Call:
        identifier = Identifier(self.advance())
        self.advance()
        if self.match(TokenType.CLOSE_PAREN):
            return Call(identifier, [])
        params = [self.expression()]
        while self.match(TokenType.COMMA):
            params.append(self.expression())
        self.consume(TokenType.CLOSE_PAREN, 'Closing parenthesis expected.')
        return Call(identifier, params)

    def identifier(self) -> Expr:
        if self.check(TokenType.OPEN_PAREN, 1):
            return self.function_call()
        return Identifier(self.advance())

    def membrane(self) -> Expr:
        identifier = Unary(self.advance(), self.expression())
        self.consume(TokenType.CLOSE_MEMBRANE, 'Close membrane expected')
        return identifier

    def channel(self) -> Expr:
        identifier = Unary(self.advance(), self.expression())
        self.consume(TokenType.CLOSE_CHANNEL, 'Close channel expected')
        return identifier

    def sinapsis(self) -> Expr:
        channel = self.channel()
        if self.check(TokenType.OPEN_MEMBRANE):
            left = self.membrane()
        else:
            left = self.identifier()
        self.consume(TokenType.THEN, 'Then expression ("-->") expected')
        if self.check(TokenType.OPEN_MEMBRANE):
            right = self.membrane()
        else:
            right = self.identifier()
        return Sinapsis(left, channel, right)

    def regex_group(self) -> Expr:
        self.advance()
        group = self.regex()
        self.consume(TokenType.CLOSE_PAREN, 'Closing parenthesis expected')
        return Grouping(group)

    def regex_expr(self) -> Optional[Expr]:
        expr = None
        if self.check(TokenType.OPEN_PAREN):
            expr = self.regex_group()
        elif self.check(TokenType.SYMBOL):
            expr = Literal(self.advance().literal)

        if expr is not None and self.match(TokenType.MULT | TokenType.PLUS):
            expr = Unary(self.peek(-1), expr)  # Habrá que ajustarlo en el interprete
        return expr

    def regex(self) -> Regex:
        expressions = []
        while expr := self.regex_expr():
            expressions.append(expr)
        return Regex(expressions)

    def production(self) -> Optional[Expr]:
        checkpoint = self.current
        try:
            return self._production()
        except:
            self.current = checkpoint
        return None

    def _production(self) -> Optional[Expr]:
        checkpoint = self.current
        if not self.check(TokenType.OPEN_MEMBRANE):
            return None
        membrane = self.membrane()
        regex = self.regex()
        if len(regex.content) == 0:
            regex = None
        if not self.match(TokenType.DIV) and (regex or self.check(TokenType.EQUAL)):
            self.current = checkpoint
            return None
        consumed = self.expression()
        if not self.match(TokenType.THEN):
            self.error(self.peek(), 'Then expression ("-->") expected')

        if self.match(TokenType.LAMBDA):
            if regex is not None:
                self.error(self.peek(), 'Forgetting rules can not have regular expression')
            return Production(membrane, regex, consumed, [], Literal(0))

        send = self.expression()
        if not self.check(TokenType.OPEN_CHANNEL):
            self.error(self.peek(), 'Channel expected')
        tuples = [(send, self.channel())]
        while self.match(TokenType.COMMA):
            send = self.expression()
            if not self.check(TokenType.OPEN_CHANNEL):
                self.error(self.peek(), 'Channel expected')
            tuples.append((send, self.channel()))

        block = Literal(0)
        if self.match(TokenType.COLON):
            block = self.expression()
        return Production(membrane, regex, consumed, tuples, block)

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        checkpoint = self.current

        if self.check(TokenType.IDENTIFIER | TokenType.OPEN_MEMBRANE):
            identifier = self.identifier() if self.check(TokenType.IDENTIFIER) else self.membrane()
            if self.check(TokenType.ASSIGNMENT):
                print("ASSIGN")
                print(*[f'{t.lexeme}({t.token_type})' for t in self.tokens[self.current:]])
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
            print("STRUCT", struct)
            return Struct(struct)


        if self.check(TokenType.IDENTIFIER):
            return self.identifier()
        if self.check(TokenType.OPEN_MEMBRANE):
            print("Membrane")
            return self.membrane()

        if self.match(TokenType.OPEN_PAREN):
            expr = self.expression()
            self.consume(TokenType.CLOSE_PAREN, 'Expected closing parenthesis.')
            return Grouping(expr)

        print("Before error: ")
        print(*[t.lexeme for t in self.tokens[self.current:]])
        self.error(self.peek(), 'Expected expression.')
