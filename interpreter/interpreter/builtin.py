from interpreter.errormanager import error
from interpreter.interpreter.memorymanager import Data, Membrane, none


def input_membrane(membrane: Data) -> Data:
    if not isinstance(membrane, Membrane):
        error('BuiltinFunction', 'ArgumentTypeMismatch', 'The argument of the input function should be a Membrane.')
    print(f'Input membrane set to [{membrane.reference}]')
    return none


def output_membrane(membrane: Data) -> Data:
    if not isinstance(membrane, Membrane):
        error('BuiltinFunction', 'ArgumentTypeMismatch', 'The argument of the output function should be a Membrane.')
    print(f'Output membrane set to [{membrane.reference}]')
    return none
