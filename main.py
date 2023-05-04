from typing import IO, List
import re

from interpreter.interpreter import Interpreter
from interpreter.parser import Parser
from interpreter.scanner import Scanner
import click

from utils import Multiset


@click.command()
@click.argument('src', type=click.File('r'))
@click.option('--input', '-i', 'inp', default=None, type=str)
@click.option('--separator', default=',', type=str)
@click.option('--no-strip', 'no_strip', is_flag=True)
@click.option('--render', '-r', is_flag=True)
@click.option('--render-path', 'render_path', default='./tmp', type=str)
def main(src: IO, inp: str, separator: str, no_strip: bool, render: bool, render_path: str):
    if inp is None:
        inp = []
    else:
        inp = inp.split(separator)

    if not no_strip:
        inp = list(map(lambda x: x.strip(), inp))

    src = src.read()

    tokens = Scanner(src).scan()
    parsed = Parser(tokens).parse()
    model = Interpreter(parsed).run()
    print(model.run(Multiset(inp), render_steps=render, render_path=render_path))


if __name__ == '__main__':
    main()
