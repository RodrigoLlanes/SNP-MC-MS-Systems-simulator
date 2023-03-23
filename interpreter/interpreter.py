from collections import defaultdict
from copy import copy
from enum import Flag, auto
from typing import Dict, List, Tuple, Optional

from interpreter.ast import Visitor, Variable, T, Unary, Literal, Grouping, Binary, Struct, Function, Expr
from interpreter.token import Token, TokenType
from utils import Multiset


class Type(Flag):
    INT = auto()
    SYMBOL = auto()
    MULTISET = auto()

    REFERENCE = auto()

    MEMBRANE = auto()
    CHANNEL = auto()

    NONE = auto()
    ERROR = auto()


class Value:
    def __init__(self, value: object, t: Type, reference: Optional[str] = None):
        self._value = value
        self.t = t
        self.reference = reference

    @property
    def value(self) -> object:
        return self._value

    @value.setter
    def value(self, value: object) -> None:
        self._value = value
        self.reference = None


class Interpreter(Visitor[Value]):
    def __init__(self, main: Function):
        self.level = 0
        self.main: Function = main
        self._memory: Dict[str, Tuple[int, Value]] = {}
        self.membranes: Dict[str, Multiset[str]] = defaultdict(Multiset[str])

    def print_state(self):
        for ref, (l, v) in self._memory.items():
            print(f'Var {ref} = {v.value} of type {v.t}')
        for ref, s in self.membranes.items():
            print(f'Membrane {ref} = {s.value}')

    def get(self, ref: str) -> Value:
        if ref in self._memory:
            var = self._memory[ref][1]
            return Value(copy(var.value), var.t, ref)
        return Value(None, Type.NONE, ref)

    def set(self, ref: str, val: Value) -> None:
        val = Value(copy(val.value), val.t)
        if ref not in self._memory:
            self._memory[ref] = (self.level, val)
        else:
            self._memory[ref] = (self._memory[ref][0], val)

    def error(self, message: str) -> Exception:
        return Exception(f'Error: {message}')

    def run(self, main: Function):
        main.accept(self)

    def visitBinaryExpr(self, expr: Binary) -> Value:
        left = expr.left.accept(self)
        right = expr.right.accept(self)
        match expr.operator.token_type:
            case TokenType.EQUAL:
                if left.reference is not None:
                    self.set(left.reference, right)
                elif right.t == Type.MULTISET:
                    self.membranes[left.value] = right
                else:
                    self.error('Only multiset can be used as a membrane value')
                return Value(None, Type.NONE)
            case TokenType.UNION:
                if left.t != Type.MULTISET or right.t != Type.MULTISET:
                    self.error('The union operator can only be used with multisets')
                return Value(left.value.union(right.value), Type.MULTISET)
            case TokenType.INTERSECTION:
                if left.t != Type.MULTISET or right.t != Type.MULTISET:
                    self.error('The intersection operator can only be used with multisets')
                return Value(left.value.intersection(right.value), Type.MULTISET)
            case TokenType.PLUS:
                if left.t == Type.MULTISET and right.t == Type.MULTISET:
                    return Value(left.value + right.value, Type.MULTISET)
                valid = Type.INT | Type.SYMBOL
                if (left.t == Type.SYMBOL or right.t == Type.SYMBOL) and (left.t in valid and right.t in valid):
                    return Value(str(left.value) + str(right.value), Type.SYMBOL)
                if left.t == Type.INT and right.t == Type.INT:
                    return Value(left.value + right.value, Type.INT)
                self.error('The + operator is not defined for types ' + left.t + ' and ' + right.t)
            case TokenType.MINUS:
                if left.t == Type.MULTISET and right.t == Type.MULTISET:
                    return Value(left.value - right.value, Type.MULTISET)
                if left.t == Type.INT and right.t == Type.INT:
                    return Value(left.value - right.value, Type.INT)
                self.error('The - operator is not defined for types ' + left.t + ' and ' + right.t)
            case TokenType.DIV:
                if left.t == Type.INT and right.t == Type.INT:
                    return Value(left.value // right.value, Type.INT)
                self.error('The - operator is not defined for types ' + left.t + ' and ' + right.t)
            case TokenType.MOD:
                if left.t == Type.INT and right.t == Type.INT:
                    return Value(left.value % right.value, Type.INT)
                self.error('The - operator is not defined for types ' + left.t + ' and ' + right.t)
            case TokenType.MULT:
                if left.t == Type.MULTISET and right.t == Type.INT:
                    return Value(left.value * right.value, Type.MULTISET)
                if left.t == Type.SYMBOL and right.t == Type.INT:
                    return Value(left.value * right.value, Type.SYMBOL)
                if left.t == Type.INT and right.t == Type.INT:
                    return Value(left.value * right.value, Type.INT)
                self.error('The - operator is not defined for types ' + left.t + ' and ' + right.t)

    def visitGroupingExpr(self, expr: Grouping) -> Value:
        return expr.expression.accept(self)

    def visitLiteralExpr(self, expr: Literal) -> Value:
        if isinstance(expr.value, str):
            return Value(expr.value, Type.SYMBOL)
        if isinstance(expr.value, int):
            return Value(expr.value, Type.INT)
        raise self.error('Unknown literal type of ' + str(expr.value))

    def visitUnaryExpr(self, expr: Unary) -> Value:
        value = expr.right.accept(self)

        if expr.operator.token_type == TokenType.MINUS:
            if value.t != Type.INT:
                raise self.error('Can not apply minus operator to a non int value')
            return Value(-value.value, Type.INT)

        if expr.operator.token_type == TokenType.OPEN_MEMBRANE:
            if value.t != Type.INT:
                raise self.error('Can not get a membrane with a non int index')
            return Value(value.value, Type.MEMBRANE)

        if expr.operator.token_type == TokenType.OPEN_CHANNEL:
            if value.t != Type.INT:
                raise self.error('Can not get a channel with a non int index')
            return Value(value.value, Type.CHANNEL)

    def visitVariableExpr(self, expr: Variable) -> Value:
        return self.get(expr.variable.lexeme)

    def visitStructExpr(self, expr: Struct) -> Value:
        m = Multiset()
        for v in expr.content:
            val = v.accept(self)
            if val.t != Type.SYMBOL:
                raise self.error('Expected multiset items to be symbol but ' + val.t + '  found')
            m.add(val.value)
        return Value(m, Type.MULTISET)

    def visitFunctionExpr(self, expr: Function) -> Value:
        from tests.testParser import Printer
        for instruction in expr.instructions:
            print("=============================================")
            print(instruction.accept(Printer()))
            instruction.accept(self)
            print("")
            self.print_state()
        return Value(None, Type.NONE)
