from typing import List, Dict

from interpreter.errormanager import error
from interpreter.token import Token, TokenType


class Scanner:
    def __init__(self, source: str) -> None:
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1
        self.source: str = source
        self.tokens: List[Token] = []

        self.keywords: Dict[str, TokenType] = {
            'lambda': TokenType.LAMBDA,
            'λ': TokenType.LAMBDA,
            #'in': TokenType.IN,
            #'out': TokenType.OUT
        }

    def error(self, msg: str) -> None:
        error('Scanner', 'SyntaxError', msg)

    def at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> chr:
        self.current += 1
        return self.source[self.current-1]

    def peek(self, d: int = 0) -> chr:
        return self.source[self.current+d]

    def match(self, expected: chr) -> bool:
        if self.at_end():
            return False
        if self.peek() != expected:
            return False
        self.current += 1
        return True

    def identifier(self) -> str:
        start = self.current
        while not self.at_end() and (self.peek().isalnum() or self.peek() == '_'):
            self.advance()
        if start == self.current:
            self.error(f'Unexpected char "{self.peek()}" after "{self.peek(-1)}" on line {self.line}.')
        return self.source[start: self.current]

    def get_string(self, closing: str) -> str:
        start = self.current
        while not self.at_end() and (self.advance() != closing):
            pass
        if start == self.current:
            self.error(f'Unexpected char "{self.peek()}" after "{self.peek(-1)}" on line {self.line}, expected a letter.')
        return self.source[start: self.current-1]

    def add_token(self, token_type: TokenType, literal: object = None, text: str = None) -> None:
        if text is None:
            text = self.source[self.start: self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def last(self) -> Token:
        return self.tokens[-1]

    def number(self) -> None:
        while not self.at_end() and self.peek().isnumeric():
            self.advance()
        self.add_token(TokenType.NUMBER, int(self.source[self.start: self.current]))

    def ignore_line(self) -> None:
        while not self.at_end():
            if self.advance() == '\n':
                self.line += 1
                break

    def next_token(self) -> None:
        c = self.advance()
        match c:
            case '(':
                self.add_token(TokenType.OPEN_PAREN)
            case ')':
                self.add_token(TokenType.CLOSE_PAREN)
            case '{':
                self.add_token(TokenType.OPEN_SET)
            case '}':
                self.add_token(TokenType.CLOSE_SET)
            case '[':
                self.add_token(TokenType.OPEN_MEMBRANE)
            case ']':
                self.add_token(TokenType.CLOSE_MEMBRANE)
            case '<':
                self.add_token(TokenType.OPEN_CHANNEL)
            case '>':
                self.add_token(TokenType.CLOSE_CHANNEL)
            case ',':
                self.add_token(TokenType.COMMA)
            case ':':
                self.add_token(TokenType.COLON)
            case '&':
                if self.match('='):
                    self.add_token(TokenType.INTERSECTION_EQUAL)
                else:
                    self.add_token(TokenType.INTERSECTION)
            case '|':
                if self.match('='):
                    self.add_token(TokenType.UNION_EQUAL)
                else:
                    self.add_token(TokenType.UNION)
            case '%':
                if self.match('='):
                    self.add_token(TokenType.MOD_EQUAL)
                else:
                    self.add_token(TokenType.MOD)
            case '*':
                if self.match('='):
                    self.add_token(TokenType.MULT_EQUAL)
                else:
                    self.add_token(TokenType.MULT)
            case '/':
                if self.match('='):
                    self.add_token(TokenType.DIV_EQUAL)
                else:
                    self.add_token(TokenType.DIV)
            case '+':
                if self.match('='):
                    self.add_token(TokenType.PLUS_EQUAL)
                else:
                    self.add_token(TokenType.PLUS)
            case '-':
                if self.peek() == '-' and self.peek(1) == '>':
                    self.advance()
                    self.advance()
                    self.add_token(TokenType.THEN)
                elif self.match('='):
                    self.add_token(TokenType.MINUS_EQUAL)
                else:
                    self.add_token(TokenType.MINUS)
            case '=':
                self.add_token(TokenType.EQUAL)
            case '#':
                self.ignore_line()
            case '\'' | '"':
                self.add_token(TokenType.SYMBOL, self.get_string(c))
            case ' ' | '\r' | '\t':
                pass
            case '\n' | ';':
                if len(self.tokens) > 0 and self.tokens[-1].token_type != TokenType.END:
                    self.add_token(TokenType.END)
                if c == '\n':
                    self.line += 1
            case _:
                if c.isnumeric():
                    self.number()
                elif c.isalpha():
                    self.current -= 1
                    string = self.identifier()
                    if string in self.keywords:
                        self.add_token(self.keywords[string], string)
                    else:
                        self.add_token(TokenType.IDENTIFIER, string)
                else:
                    self.error(f'Unknown char "{c}" on line {self.line}')

    def scan(self) -> List[Token]:
        while not self.at_end():
            self.start = self.current
            self.next_token()

        self.tokens.append(Token(TokenType.EOF, 'EOF', None, self.line))
        return self.tokens
