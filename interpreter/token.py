from enum import auto, Enum


class TokenType(Enum):
    DEF = auto()
    CALL = auto()

    IDENTIFIER = auto()
    PROPERTY = auto()
    SYMBOL = auto()
    NUMBER = auto()
    LABEL = auto()

    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()

    MINUS = auto()
    PLUS = auto()
    MULT = auto()
    DIV = auto()
    MOD = auto()
    THEN = auto()

    EQUAL = auto()
    PLUS_EQUAL = auto()

    SEMICOLON = auto()
    COMMA = auto()

    EOF = auto()


class Token:
    def __init__(self, token_type: TokenType, lexeme: str, literal: object, line: int) -> None:
        self.token_type: TokenType = token_type
        self.lexeme: str = lexeme
        self.literal: object = literal
        self.line: int = line

    def __str__(self):
        return f'{self.token_type} {self.lexeme} {self.literal}'

