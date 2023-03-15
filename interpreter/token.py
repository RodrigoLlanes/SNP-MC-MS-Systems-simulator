from enum import auto, Enum


class TokenType(Enum):
    DEF = auto()    # FUTURE
    RETURN = auto()    # FUTURE

    IN = auto()
    OUT = auto()

    IDENTIFIER = auto()
    SYMBOL = auto()
    NUMBER = auto()

    OPEN_PAREN = auto()
    CLOSE_PAREN = auto()
    OPEN_SET = auto()
    CLOSE_SET = auto()
    OPEN_MEMBRANE = auto()
    CLOSE_MEMBRANE = auto()
    OPEN_CHANNEL = auto()
    CLOSE_CHANNEL = auto()

    MINUS = auto()
    PLUS = auto()
    MULT = auto()
    DIV = auto()
    MOD = auto()
    UNION = auto()
    INTERSECTION = auto()
    THEN = auto()

    EQUAL = auto()
    PLUS_EQUAL = auto()
    MINUS_EQUAL = auto()
    MULT_EQUAL = auto()
    DIV_EQUAL = auto()
    MOD_EQUAL = auto()
    UNION_EQUAL = auto()
    INTERSECTION_EQUAL = auto()

    END = auto()
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

