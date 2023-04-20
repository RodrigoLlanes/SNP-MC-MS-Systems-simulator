import re
import argparse
from typing import Tuple, List, Dict, TextIO


class ASTGenerator:
    @staticmethod
    def parse_input(input_path: str) -> Dict[str, List[Tuple[str, str]]]:
        ast = {}
        with open(input_path, 'r') as file:
            for line in file.readlines():
                line = line.strip()
                if len(line) == 0:
                    continue
                class_name, fields = map(str.strip, line.split(':'))
                fields = list(map(lambda field: re.split(r'\s(?!(?:[^\s\[\]]+,)*[^\s\[\]]+])', field.strip(), 0),
                                  re.split(r',(?!(?:[^,\[\]]+,)*[^,\[\]]+])', fields, 0)))
                ast[class_name] = fields
        return ast

    def __init__(self, input_path: str, base_name: str = 'Expr'):
        self.ast: Dict[str, List[Tuple[str, str]]] = self.parse_input(input_path)
        self.base: str = base_name

    def define_type(self, out: TextIO, name: str, fields: List[Tuple[str, str]]):
        field_types, field_names = zip(*fields)
        python_fields = [f'{name}: {t}' for t, name in fields]

        out.write(f'\n\nclass {name}({self.base}):\n')
        out.write(f'    def __init__(self, {", ".join(python_fields)}) -> None:\n')
        for i, field in enumerate(python_fields):
            out.write(f'        self.{field} = {field_names[i]}\n')
        out.write(f'\n    def accept(self, visitor: Visitor[T]) -> T:\n')
        out.write(f'        return visitor.visit{name}{self.base}(self)\n')

    def define_visitor(self, out: TextIO):
        out.write('class Visitor(abc.ABC, Generic[T]):')
        for t in self.ast.keys():
            out.write('\n    @abc.abstractmethod\n')
            out.write(f'    def visit{t}{self.base}(self, {self.base.lower()}: {t}) -> T:\n')
            out.write('        raise NotImplementedError()\n')
        out.write('\n\n')


    def write(self, output_path: str, header: str = '') -> None:
        with open(output_path, 'w') as file:
            file.write(f'from __future__ import annotations\n\n')
            file.write(f'from typing import Generic, TypeVar\nimport abc\n')
            file.write(f'\n{header}\n\n\n')
            file.write('T = TypeVar(\'T\')\n\n\n')
            self.define_visitor(file)
            file.write(f'class {self.base}:\n')
            file.write(f'    def accept(self, visitor: Visitor[T]) -> T:\n')
            file.write(f'        raise NotImplementedError()\n')
            for name, fields in self.ast.items():
                self.define_type(file, name, fields)


def main():
    parser = argparse.ArgumentParser(description='Abstract syntax tree generator')
    parser.add_argument('input', type=str, help='Input file path')
    parser.add_argument('output', type=str, help='Output file path')
    parser.add_argument('-b', '--base', type=str, help='Base expression name', required=False, default='Expr')
    parser.add_argument('-i', '--header', type=str, help='File header, put hear the required imports or desired comments', required=False, default='')
    args = parser.parse_args()

    generator = ASTGenerator(args.input, args.base)
    generator.write(args.output, re.sub(r"\\n", "\n", args.header))


if __name__ == '__main__':
    main()
