import sys
from enum import Enum, auto

from interpreter.ast import Visitor, Identifier, T, Unary, Literal, Grouping, Binary, Struct
from interpreter.token import Token


class Type(Enum):
    INT = auto()
    SYMBOL = auto()
    MULTISET = auto()
    STRUCTURE = auto()
    NONE = auto()
    ERROR = auto()


class TypeChecker(Visitor[Type]):
    def __init__(self):
        self.labels = {}
        self.variables = {}
        self.properties = {}

    def error(self, token: Token, msg: str):
        return print(f'(line: {token.line}) error at {token.lexeme}: {msg}', file=sys.stderr)

    def visitStructExpr(self, expr: Struct) -> Type:
        err = False
        for elem in expr.content:
            if elem.accept(self) != Type.STRUCTURE and elem.accept(self) != Type.ERROR:
                self.error('Expected structure.')
                err = True

        if expr.identifier.literal in self.labels:
            self.error(expr.identifier, 'Label redefinition.')
            err = True
        else:
            self.labels[expr.identifier.literal] = expr

        if err:
            return Type.ERROR
        return Type.STRUCTURE

    def visitBinaryExpr(self, expr: Binary) -> Type:
        pass

    def visitGroupingExpr(self, expr: Grouping) -> Type:
        return expr.accept(self)

    def visitLiteralExpr(self, expr: Literal) -> Type:
        if isinstance(expr.value, int):
            return Type.INT
        if isinstance(expr.value, str):
            return Type.SYMBOL
        # TODO: Este error no se debería mostrar nunca.
        self.error('Unknown literal type.')
        return Type.ERROR

    def visitUnaryExpr(self, expr: Unary) -> Type:
        pass

    def visitVariableExpr(self, expr: Identifier) -> Type:
        pass