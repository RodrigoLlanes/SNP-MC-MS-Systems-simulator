from typing import List, Dict

from interpreter.token import Token, TokenType


class Scanner:
    def __init__(self, source: str) -> None:
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1
        self.source: str = source
        self.tokens: List[Token] = []

        self.keywords: Dict[str, TokenType] = {
            'def': TokenType.DEF,
            'call': TokenType.CALL
        }

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

    def get_string(self) -> str:
        while not self.at_end() and (self.peek().isalnum() or self.peek() == '_'):
            self.advance()
        return self.source[self.start: self.current]

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

    def identifier(self) -> None:
        string = self.get_string()
        if string in self.keywords:
            self.add_token(self.keywords[string], string)
        elif self.last().token_type in (TokenType.CALL, TokenType.DEF):
            self.add_token(TokenType.IDENTIFIER, string)
        else:
            for s in string:
                self.add_token(TokenType.SYMBOL, s, text=s)

    def ignore_line(self) -> None:
        while not self.at_end():
            if self.advance() == '\n':
                self.line += 1
                break

    def next_token(self) -> None:
        c = self.advance()
        match c:
            case '(':
                self.add_token(TokenType.LEFT_PAREN)
            case ')':
                self.add_token(TokenType.RIGHT_PAREN)
            case '[':
                self.add_token(TokenType.LEFT_BRACE)
            case ']':
                self.add_token(TokenType.RIGHT_BRACE)
            case '{':
                self.add_token(TokenType.LEFT_BRACKET)
            case '}':
                self.add_token(TokenType.RIGHT_BRACKET)
            case ',':
                self.add_token(TokenType.COMMA)
            case ';':
                self.add_token(TokenType.SEMICOLON)
            case '%':
                self.add_token(TokenType.MOD)
            case '*':
                self.add_token(TokenType.MULT)
            case '=':
                self.add_token(TokenType.EQUAL)
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
                else:
                    self.add_token(TokenType.MINUS)
            case '/':
                if self.match('/'):
                    self.ignore_line()
                else:
                    self.add_token(TokenType.DIV)
            case ' ' | '\r' | '\t':
                pass
            case '\n':
                self.line += 1
            case _:
                if c.isnumeric():
                    self.number()
                elif c.isalpha():
                    self.identifier()
                elif c == '\'':
                    self.start += 1
                    self.add_token(TokenType.LABEL, self.get_string())
                elif c == '@':
                    self.start += 1
                    self.add_token(TokenType.PROPERTY, self.get_string())
                else:
                    raise Exception(f'Unknown char "{c}" on line {self.line}')

    def scan(self) -> List[Token]:
        while not self.at_end():
            self.start = self.current
            self.next_token()

        self.tokens.append(Token(TokenType.EOF, '', None, self.line))
        return self.tokens
