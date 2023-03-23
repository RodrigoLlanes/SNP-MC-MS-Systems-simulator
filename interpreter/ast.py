from __future__ import annotations

from typing import Generic, TypeVar
import abc

from .token import Token
from typing import List

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
    def visitVariableExpr(self, expr: Variable) -> T:
        raise NotImplementedError()

    @abc.abstractmethod
    def visitStructExpr(self, expr: Struct) -> T:
        raise NotImplementedError()

    @abc.abstractmethod
    def visitFunctionExpr(self, expr: Function) -> T:
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


class Variable(Expr):
    def __init__(self, variable: Token) -> None:
        self.variable: Token = variable

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visitVariableExpr(self)


class Struct(Expr):
    def __init__(self, content: List[Expr]) -> None:
        self.content: List[Expr] = content

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visitStructExpr(self)


class Function(Expr):
    def __init__(self, identifier: Token, parameters: List[Variable], instructions: List[Expr]) -> None:
        self.identifier: Token = identifier
        self.parameters: List[Variable] = parameters
        self.instructions: List[Expr] = instructions

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visitFunctionExpr(self)
