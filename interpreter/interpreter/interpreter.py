from interpreter.ast import Visitor, Identifier, Unary, Literal, Grouping, Binary, Struct, Function, Call, Sinapsis, \
    Production, T, Regex
from interpreter.interpreter.builtin import input_membrane
from interpreter.interpreter.function import BuiltinFunction
from interpreter.interpreter.memorymanager import MemoryManager, DataType, Data, Value, Membrane, Variable, none
from interpreter.token import TokenType
from interpreter.errormanager import error
from simulator.snpsystem import SNPSystem
from tests.testParser import Printer
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
        self.mm.add_reserved('input', Value(BuiltinFunction(input_membrane(self)), DataType.FUNCTION))
        self.mm.add_reserved('out', Membrane(self.mm, 'out'))
        self.model = SNPSystem()

    def print_state(self):
        self.mm.print_state()

    def run(self) -> SNPSystem:
        self.model = SNPSystem()
        self.model.set_output('out')
        self.main.accept(self)
        for membrane, content in self.mm._membranes.items():
            self.model.add_symbols(membrane, *list(content))
        return self.model

    def calc(self, left: Data, op: TokenType, right: Data) -> Data:
        match op:
            case TokenType.UNION | TokenType.UNION_EQUAL:
                if DataType.MULTISET not in left.type or DataType.MULTISET not in right.type:
                    self.type_error('The union operator can only be used with multisets')
                return Value(left.value.union(right.value), DataType.MULTISET)
            case TokenType.INTERSECTION | TokenType.INTERSECTION_EQUAL:
                if DataType.MULTISET not in left.type or DataType.MULTISET not in right.type:
                    self.type_error('The intersection operator can only be used with multisets')
                return Value(left.value.intersection(right.value), DataType.MULTISET)
            case TokenType.PLUS | TokenType.PLUS_EQUAL:
                if DataType.MULTISET in left.type and DataType.MULTISET in right.type:
                    return Value(left.value + right.value, DataType.MULTISET)
                valid = DataType.INT | DataType.SYMBOL
                if (DataType.SYMBOL in left.type or DataType.SYMBOL in right.type) and ((left.type & valid) and (right.type & valid)):
                    return Value(str(left.value) + str(right.value), DataType.SYMBOL)
                if DataType.INT in left.type and DataType.INT in right.type:
                    return Value(left.value + right.value, DataType.INT)
                self.type_error(f'The + operator is not defined for {left.type} and {right.type}')
            case TokenType.MINUS | TokenType.MINUS_EQUAL:
                if DataType.MULTISET in left.type and DataType.MULTISET in right.type:
                    return Value(left.value - right.value, DataType.MULTISET)
                if DataType.INT in left.type and DataType.INT in right.type:
                    return Value(left.value - right.value, DataType.INT)
                self.type_error(f'The - operator is not defined for {left.type} and {right.type}')
            case TokenType.DIV | TokenType.DIV_EQUAL:
                if DataType.INT in left.type and DataType.INT in right.type:
                    return Value(left.value // right.value, DataType.INT)
                self.type_error(f'The - operator is not defined for {left.type} and {right.type}')
            case TokenType.MOD | TokenType.MOD_EQUAL:
                if DataType.INT in left.type and DataType.INT in right.type:
                    return Value(left.value % right.value, DataType.INT)
                self.type_error(f'The - operator is not defined for {left.type} and {right.type}')
            case TokenType.MULT | TokenType.MULT_EQUAL:
                if DataType.MULTISET in left.type and DataType.INT in right.type:
                    return Value(left.value * right.value, DataType.MULTISET)
                if DataType.SYMBOL in left.type and DataType.INT in right.type:
                    return Value(left.value * right.value, DataType.SYMBOL)
                if DataType.INT in left.type and DataType.INT in right.type:
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
        if DataType.REGEX in value.type:
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
            if DataType.INT not in value.type:
                self.type_error('Can not apply minus operator to a non int value')
            return Value(-value.value, DataType.INT)

        if expr.operator.token_type == TokenType.OPEN_MEMBRANE:
            if DataType.INT not in value.type:
                self.type_error('Can not get a membrane with a non int index')
            return Membrane(self.mm, value.value)

        if expr.operator.token_type == TokenType.OPEN_CHANNEL:
            if DataType.INT not in value.type:
                self.type_error('Can not get a channel with a non int index')
            return Value(value.value, DataType.CHANNEL)

        if expr.operator.token_type == TokenType.MULT:
            if DataType.SYMBOL in value.type:
                return Value([value.value, '*'], DataType.REGEX)
            if DataType.REGEX in value.type:
                return Value(value.value + ['*'], DataType.REGEX)
            self.type_error('Can not use the star regex operator with non regex or symbol expression')

        if expr.operator.token_type == TokenType.PLUS:
            if DataType.SYMBOL in value.type:
                return Value([value.value, '+'], DataType.REGEX)
            if DataType.REGEX in value.type:
                return Value(value.value + ['+'], DataType.REGEX)
            self.type_error('Can not use the plus regex operator with non regex or symbol expression')

        self.unexpected_error(f'Unknown unary operator {expr.operator.token_type}')

    def visitIdentifierExpr(self, expr: Identifier) -> Data:
        return Variable(self.mm, expr.identifier.lexeme)

    def visitStructExpr(self, expr: Struct) -> Data:
        m = Multiset()
        for v in expr.content:
            val = v.accept(self)
            if DataType.SYMBOL not in val.type:
                self.type_error(f'Expected multiset items to be symbol but {val.type} found')
            m.add(val.value)
        return Value(m, DataType.MULTISET)

    def visitFunctionExpr(self, expr: Function) -> Data:
        #from tests.testParser import Printer
        for instruction in expr.instructions:
            #print("=============================================")
            instruction.accept(self)
            #print("")
            #self.print_state()
        return Value(None, DataType.INT)

    def visitCallExpr(self, expr: Call) -> Data:
        f = expr.identifier.accept(self)
        if DataType.FUNCTION not in f.type:
            self.type_error(f'Expected function but {f.type} found')
        parameters = list(map(lambda x: x.accept(self), expr.params))
        return f.value.call(*parameters)

    def visitSinapsisExpr(self, expr: Sinapsis) -> Data:
        left = expr.left.accept(self)
        right = expr.right.accept(self)
        channel = expr.channel.accept(self)
        if DataType.MEMBRANE not in left.type:
            self.type_error(f'Expected membrane as left production part but {left.type} found')
        if DataType.MEMBRANE not in right.type:
            self.type_error(f'Expected membrane as right production part but {right.type} found')

        if channel.type != DataType.CHANNEL:
            self.type_error(f'Expected channel as production label but {channel.type} found')

        if right.reference == left.reference:
            self.interpreter_error('CircularSinapsisError', 'Circular sinapsis can not exist')

        if left.reference == 'out':
            self.interpreter_error('EnvValueError', f'Sinapsis origin can not be the output environment')

        self.model.add_channel(channel.value, left.reference, right.reference)
        return none

    def visitRegexExpr(self, expr: Regex) -> Data:
        regex = []
        for val in map(lambda x: x.accept(self), expr.content):
            if DataType.SYMBOL in val.type:
                regex.append(val.value)
            elif DataType.REGEX in val.type:
                regex += val.value
            else:
                self.type_error(f'Expected regex or symbol but {val.type} found')
        return Value(regex, DataType.REGEX)

    def visitProductionExpr(self, expr: Production) -> Data:
        membrane = expr.membrane.accept(self)
        regex = expr.regex.accept(self).value if expr.regex else None
        consumed = expr.consumed.accept(self)
        channels = [(send.accept(self), channel.accept(self)) for send, channel in expr.channels]
        block = expr.block.accept(self).value

        #print(f'New production added to membrane {membrane.reference} if match {regex.value} consume {consumed.value}')
        #for send, channel in channels:
        #    print(f'    Send {send.value} to channel {channel.value}')
        self.model.add_rule(membrane.reference, regex, consumed.value, {channel.value: send.value for send, channel in channels}, block)
        return none
