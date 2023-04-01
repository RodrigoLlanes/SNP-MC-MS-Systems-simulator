from collections import defaultdict
from copy import copy
from enum import Flag, auto
from typing import Dict, List, Tuple, Optional

from interpreter.ast import Visitor, Identifier, T, Unary, Literal, Grouping, Binary, Struct, Function, Expr
from interpreter.memorymanager import MemoryManager, DataType, Data, Value, Membrane, Variable
from interpreter.token import Token, TokenType
from utils import Multiset


class Interpreter(Visitor[Data]):
    def __init__(self, main: Function):
        self.mm = MemoryManager()
        self.main: Function = main

    def print_state(self):
        self.mm.print_state()

    def error(self, message: str) -> Exception:
        return Exception(f'Error: {message}')

    def run(self, main: Function):
        main.accept(self)

    def visitBinaryExpr(self, expr: Binary) -> Data:
        left = expr.left.accept(self)
        right = expr.right.accept(self)
        match expr.operator.token_type:
            case TokenType.EQUAL:
                left.value = right
                return left
            case TokenType.UNION:
                if left.type != DataType.MULTISET or right.type != DataType.MULTISET:
                    self.error('The union operator can only be used with multisets')
                return Value(left.value.union(right.value), DataType.MULTISET)
            case TokenType.INTERSECTION:
                if left.type != DataType.MULTISET or right.type != DataType.MULTISET:
                    self.error('The intersection operator can only be used with multisets')
                return Value(left.value.intersection(right.value), DataType.MULTISET)
            case TokenType.PLUS:
                if left.type == DataType.MULTISET and right.type == DataType.MULTISET:
                    return Value(left.value + right.value, DataType.MULTISET)
                valid = DataType.INT | DataType.SYMBOL
                if (left.type == DataType.SYMBOL or right.type == DataType.SYMBOL) and (left.type in valid and right.type in valid):
                    return Value(str(left.value) + str(right.value), DataType.SYMBOL)
                if left.type == DataType.INT and right.type == DataType.INT:
                    return Value(left.value + right.value, DataType.INT)
                self.error('The + operator is not defined for DataTypes ' + left.type + ' and ' + right.type)
            case TokenType.MINUS:
                if left.type == DataType.MULTISET and right.type == DataType.MULTISET:
                    return Value(left.value - right.value, DataType.MULTISET)
                if left.type == DataType.INT and right.type == DataType.INT:
                    return Value(left.value - right.value, DataType.INT)
                self.error('The - operator is not defined for DataTypes ' + left.type + ' and ' + right.type)
            case TokenType.DIV:
                if left.type == DataType.INT and right.type == DataType.INT:
                    return Value(left.value // right.value, DataType.INT)
                self.error('The - operator is not defined for DataTypes ' + left.type + ' and ' + right.type)
            case TokenType.MOD:
                if left.type == DataType.INT and right.type == DataType.INT:
                    return Value(left.value % right.value, DataType.INT)
                self.error('The - operator is not defined for DataTypes ' + left.type + ' and ' + right.type)
            case TokenType.MULT:
                if left.type == DataType.MULTISET and right.type == DataType.INT:
                    return Value(left.value * right.value, DataType.MULTISET)
                if left.type == DataType.SYMBOL and right.type == DataType.INT:
                    return Value(left.value * right.value, DataType.SYMBOL)
                if left.type == DataType.INT and right.type == DataType.INT:
                    return Value(left.value * right.value, DataType.INT)
                self.error('The - operator is not defined for DataTypes ' + left.type + ' and ' + right.type)

    def visitGroupingExpr(self, expr: Grouping) -> Data:
        return expr.expression.accept(self)

    def visitLiteralExpr(self, expr: Literal) -> Data:
        if isinstance(expr.value, str):
            return Value(expr.value, DataType.SYMBOL)
        if isinstance(expr.value, int):
            return Value(expr.value, DataType.INT)
        raise self.error('Unknown literal DataType of ' + str(expr.value))

    def visitUnaryExpr(self, expr: Unary) -> Data:
        value = expr.right.accept(self)

        if expr.operator.token_type == TokenType.MINUS:
            if value.type != DataType.INT:
                raise self.error('Can not apply minus operator to a non int value')
            return Value(-value.value, DataType.INT)

        if expr.operator.token_type == TokenType.OPEN_MEMBRANE:
            if value.type != DataType.INT:
                raise self.error('Can not get a membrane with a non int index')
            return Membrane(self.mm, value.value)

    def visitVariableExpr(self, expr: Identifier) -> Data:
        return Variable(self.mm, expr.identifier.lexeme)

    def visitStructExpr(self, expr: Struct) -> Data:
        m = Multiset()
        for v in expr.content:
            val = v.accept(self)
            if val.type != DataType.SYMBOL:
                raise self.error('Expected multiset items to be symbol but ' + val.type + '  found')
            m.add(val.value)
        return Value(m, DataType.MULTISET)

    def visitFunctionExpr(self, expr: Function) -> Data:
        from tests.testParser import Printer
        for instruction in expr.instructions:
            print("=============================================")
            print(instruction.accept(Printer()))
            instruction.accept(self)
            print("")
            self.print_state()
        return Value(None, DataType.INT)
