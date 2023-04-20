from __future__ import annotations

from typing import Generic, TypeVar
import abc

from .token import Token
from typing import List, Tuple


T = TypeVar('T')


class Visitor(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def visitBinaryExpr(self, expr: Binary) -> T:
        raise NotImplementedError()

    @abc.abstractmethod
    def visitGroupingExpr(self, expr: Grouping) -> T:
        raise NotImplementedError()

    @abc.abstractmethod
    def visitLiteralExpr(self, expr: Literal) -> T:
        raise NotImplementedError()

    @abc.abstractmethod
    def visitUnaryExpr(self, expr: Unary) -> T:
        raise NotImplementedError()

    @abc.abstractmethod
    def visitIdentifierExpr(self, expr: Identifier) -> T:
        raise NotImplementedError()

    @abc.abstractmethod
    def visitStructExpr(self, expr: Struct) -> T:
        raise NotImplementedError()

    @abc.abstractmethod
    def visitCallExpr(self, expr: Call) -> T:
        raise NotImplementedError()

    @abc.abstractmethod
    def visitFunctionExpr(self, expr: Function) -> T:
        raise NotImplementedError()

    @abc.abstractmethod
    def visitSinapsisExpr(self, expr: Sinapsis) -> T:
        raise NotImplementedError()

    @abc.abstractmethod
    def visitRegexExpr(self, expr: Regex) -> T:
        raise NotImplementedError()

    @abc.abstractmethod
    def visitProductionExpr(self, expr: Production) -> T:
        raise NotImplementedError()


class Expr:
    def accept(self, visitor: Visitor[T]) -> T:
        raise NotImplementedError()


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left: Expr = left
        self.operator: Token = operator
        self.right: Expr = right

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visitBinaryExpr(self)


class Grouping(Expr):
    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visitGroupingExpr(self)


class Literal(Expr):
    def __init__(self, value: object) -> None:
        self.value: object = value

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visitLiteralExpr(self)


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr) -> None:
        self.operator: Token = operator
        self.right: Expr = right

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visitUnaryExpr(self)


class Identifier(Expr):
    def __init__(self, identifier: Token) -> None:
        self.identifier: Token = identifier

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visitIdentifierExpr(self)


class Struct(Expr):
    def __init__(self, content: List[Expr]) -> None:
        self.content: List[Expr] = content

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visitStructExpr(self)


class Call(Expr):
    def __init__(self, identifier: Identifier, params: List[Expr]) -> None:
        self.identifier: Identifier = identifier
        self.params: List[Expr] = params

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visitCallExpr(self)


class Function(Expr):
    def __init__(self, identifier: Token, parameters: List[Token], instructions: List[Expr]) -> None:
        self.identifier: Token = identifier
        self.parameters: List[Token] = parameters
        self.instructions: List[Expr] = instructions

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visitFunctionExpr(self)


class Sinapsis(Expr):
    def __init__(self, left: Expr, channel: Expr, right: Expr) -> None:
        self.left: Expr = left
        self.channel: Expr = channel
        self.right: Expr = right

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visitSinapsisExpr(self)


class Regex(Expr):
    def __init__(self, content: List[Expr]) -> None:
        self.content: List[Expr] = content

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visitRegexExpr(self)


class Production(Expr):
    def __init__(self, membrane: Expr, regex: Expr, consumed: Expr, channels: List[Tuple[Expr, Expr]]) -> None:
        self.membrane: Expr = membrane
        self.regex: Expr = regex
        self.consumed: Expr = consumed
        self.channels: List[Tuple[Expr, Expr]] = channels

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visitProductionExpr(self)
