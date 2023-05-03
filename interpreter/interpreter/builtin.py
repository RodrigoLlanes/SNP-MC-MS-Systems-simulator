from interpreter.errormanager import error
from interpreter.interpreter.memorymanager import Data, Membrane, none


def input_membrane(interpreter: 'Interpreter'):
    def wrapper(membrane: Data) -> Data:
        if not isinstance(membrane, Membrane):
            error('BuiltinFunction', 'ArgumentTypeMismatch', 'The argument of the input function should be a Membrane.')
        interpreter.model.set_input(membrane.reference)
        return none
    return wrapper


def output_membrane(interpreter: 'Interpreter'):
    def wrapper(membrane: Data) -> Data:
        if not isinstance(membrane, Membrane):
            error('BuiltinFunction', 'ArgumentTypeMismatch', 'The argument of the output function should be a Membrane.')
        interpreter.model.set_output(membrane.reference)
        return none
    return wrapper
