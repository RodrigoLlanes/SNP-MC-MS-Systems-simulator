from interpreter.ast import Visitor, Identifier, Unary, Literal, Grouping, Binary, Struct, Function, Call, Sinapsis, \
    Production, T, Regex
from interpreter.interpreter.builtin import input_membrane, output_membrane
from interpreter.interpreter.function import BuiltinFunction
from interpreter.interpreter.memorymanager import MemoryManager, DataType, Data, Value, Membrane, Variable, none
from interpreter.token import TokenType
from interpreter.errormanager import error
from utils import Multiset


class Interpreter(Visitor[Data]):
    @staticmethod
    def interpreter_error(error_type: str, msg: str) -> None:
        error('interpreter', error_type, msg)

    @staticmethod
    def type_error(msg: str) -> None:
        Interpreter.interpreter_error('TypeError', msg)

    @staticmethod
    def unexpected_error(msg: str) -> None:
        Interpreter.interpreter_error('UnexpectedError', msg)

    def __init__(self, main: Function):
        self.mm = MemoryManager()
        self.main: Function = main

        # Register Builtin functions
        self.mm.set_var('input', Value(BuiltinFunction(input_membrane), DataType.FUNCTION))
        self.mm.set_var('output', Value(BuiltinFunction(output_membrane), DataType.FUNCTION))

    def print_state(self):
        self.mm.print_state()

    def run(self):
        self.main.accept(self)

    def calc(self, left: Data, op: TokenType, right: Data) -> Data:
        match op:
            case TokenType.UNION | TokenType.UNION_EQUAL:
                if left.type != DataType.MULTISET or right.type != DataType.MULTISET:
                    self.type_error('The union operator can only be used with multisets')
                return Value(left.value.union(right.value), DataType.MULTISET)
            case TokenType.INTERSECTION | TokenType.INTERSECTION_EQUAL:
                if left.type != DataType.MULTISET or right.type != DataType.MULTISET:
                    self.type_error('The intersection operator can only be used with multisets')
                return Value(left.value.intersection(right.value), DataType.MULTISET)
            case TokenType.PLUS | TokenType.PLUS_EQUAL:
                if left.type == DataType.MULTISET and right.type == DataType.MULTISET:
                    return Value(left.value + right.value, DataType.MULTISET)
                valid = DataType.INT | DataType.SYMBOL
                if (left.type == DataType.SYMBOL or right.type == DataType.SYMBOL) and (
                        left.type in valid and right.type in valid):
                    return Value(str(left.value) + str(right.value), DataType.SYMBOL)
                if left.type == DataType.INT and right.type == DataType.INT:
                    return Value(left.value + right.value, DataType.INT)
                self.type_error(f'The + operator is not defined for {left.type} and {right.type}')
            case TokenType.MINUS | TokenType.MINUS_EQUAL:
                if left.type == DataType.MULTISET and right.type == DataType.MULTISET:
                    return Value(left.value - right.value, DataType.MULTISET)
                if left.type == DataType.INT and right.type == DataType.INT:
                    return Value(left.value - right.value, DataType.INT)
                self.type_error(f'The - operator is not defined for {left.type} and {right.type}')
            case TokenType.DIV | TokenType.DIV_EQUAL:
                if left.type == DataType.INT and right.type == DataType.INT:
                    return Value(left.value // right.value, DataType.INT)
                self.type_error(f'The - operator is not defined for {left.type} and {right.type}')
            case TokenType.MOD | TokenType.MOD_EQUAL:
                if left.type == DataType.INT and right.type == DataType.INT:
                    return Value(left.value % right.value, DataType.INT)
                self.type_error(f'The - operator is not defined for {left.type} and {right.type}')
            case TokenType.MULT | TokenType.MULT_EQUAL:
                if left.type == DataType.MULTISET and right.type == DataType.INT:
                    return Value(left.value * right.value, DataType.MULTISET)
                if left.type == DataType.SYMBOL and right.type == DataType.INT:
                    return Value(left.value * right.value, DataType.SYMBOL)
                if left.type == DataType.INT and right.type == DataType.INT:
                    return Value(left.value * right.value, DataType.INT)
                self.type_error(f'The - operator is not defined for {left.type} and {right.type}')
        self.unexpected_error('Unknown operand ' + op)

    def visitBinaryExpr(self, expr: Binary) -> Data:
        left = expr.left.accept(self)
        right = expr.right.accept(self)
        match expr.operator.token_type:
            case TokenType.EQUAL:
                left.value = right
                return left
            case TokenType.EQUAL | TokenType.PLUS_EQUAL | TokenType.MINUS_EQUAL | TokenType.MULT_EQUAL | TokenType.DIV_EQUAL | TokenType.MOD_EQUAL | TokenType.UNION_EQUAL | TokenType.INTERSECTION_EQUAL:
                left.value = self.calc(left, expr.operator.token_type, right)
                return left
            case _:
                return self.calc(left, expr.operator.token_type, right)

    def visitGroupingExpr(self, expr: Grouping) -> Data:
        value = expr.expression.accept(self)
        if value.type == DataType.REGEX:
            return Value(['('] + value.value + [')'], DataType.REGEX)
        return expr.expression.accept(self)

    def visitLiteralExpr(self, expr: Literal) -> Data:
        if isinstance(expr.value, str):
            return Value(expr.value, DataType.SYMBOL)
        if isinstance(expr.value, int):
            return Value(expr.value, DataType.INT)
        self.unexpected_error('Unknown literal DataType of ' + str(expr.value))

    def visitUnaryExpr(self, expr: Unary) -> Data:
        value = expr.right.accept(self)

        if expr.operator.token_type == TokenType.MINUS:
            if value.type != DataType.INT:
                self.type_error('Can not apply minus operator to a non int value')
            return Value(-value.value, DataType.INT)

        if expr.operator.token_type == TokenType.OPEN_MEMBRANE:
            if value.type != DataType.INT:
                self.type_error('Can not get a membrane with a non int index')
            return Membrane(self.mm, value.value)

        if expr.operator.token_type == TokenType.OPEN_CHANNEL:
            if value.type != DataType.INT:
                self.type_error('Can not get a channel with a non int index')
            return Value(value.value, DataType.CHANNEL)

        if expr.operator.token_type == TokenType.MULT:
            if value.type == DataType.SYMBOL:
                return Value([value.value, '*'], DataType.REGEX)
            if value.type == DataType.REGEX:
                return Value(value.value + ['*'], DataType.REGEX)
            self.type_error('Can not use the star regex operator with non regex or symbol expression')

        if expr.operator.token_type == TokenType.PLUS:
            if value.type == DataType.SYMBOL:
                return Value([value.value, '+'], DataType.REGEX)
            if value.type == DataType.REGEX:
                return Value(value.value + ['+'], DataType.REGEX)
            self.type_error('Can not use the plus regex operator with non regex or symbol expression')

        self.unexpected_error(f'Unknown unary operator {expr.operator.token_type}')

    def visitIdentifierExpr(self, expr: Identifier) -> Data:
        return Variable(self.mm, expr.identifier.lexeme)

    def visitStructExpr(self, expr: Struct) -> Data:
        m = Multiset()
        for v in expr.content:
            val = v.accept(self)
            if val.type != DataType.SYMBOL:
                self.type_error(f'Expected multiset items to be symbol but {val.type} found')
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

    def visitCallExpr(self, expr: Call) -> Data:
        f = expr.identifier.accept(self)
        if f.type != DataType.FUNCTION:
            self.type_error(f'Expected function but {f.type} found')
        parameters = list(map(lambda x: x.accept(self), expr.params))
        return f.value.call(*parameters)

    def visitSinapsisExpr(self, expr: Sinapsis) -> Data:
        left = expr.left.accept(self)
        right = expr.right.accept(self)
        channel = expr.channel.accept(self)
        if not isinstance(left, Membrane):
            self.type_error(f'Expected membrane as left production part but {left.type} found')
        if not isinstance(right, Membrane):
            self.type_error(f'Expected membrane as right production part but {right.type} found')
        if channel.type != DataType.CHANNEL:
            self.type_error(f'Expected channel as production label but {channel.type} found')
        print(f'New sinapsis added to channel {channel.value} from membrane {left.reference} to membrane {right.reference}')
        return none

    def visitRegexExpr(self, expr: Regex) -> Data:
        regex = []
        for val in map(lambda x: x.accept(self), expr.content):
            if val.type == DataType.SYMBOL:
                regex.append(val.value)
            elif val.type == DataType.REGEX:
                regex += val.value
            else:
                self.type_error(f'Expected regex or symbol but {val.type} found')
        return Value(regex, DataType.REGEX)

    def visitProductionExpr(self, expr: Production) -> Data:
        membrane = expr.membrane.accept(self)
        regex = expr.regex.accept(self)
        consumed = expr.consumed.accept(self)
        channels = [(send.accept(self), channel.accept(self)) for send, channel in expr.channels]

        print(f'New production added to membrane {membrane.reference} if match {regex.value} consume {consumed.value}')
        for send, channel in channels:
            print(f'    Send {send.value} to channel {channel.value}')
        return none
