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
@click.option('--render', is_flag=True)
@click.option('--render-path', 'render_path', default='./tmp', type=str)
@click.option('--repeat', '-r', default=1, type=int)
@click.option('--mode', '-m', default='halt', type=click.Choice(['halt', 'halt-mc', 'time', 'time-mc']))
@click.option('--max-steps', 'max_steps', default=None, type=int)
def main(src: IO, inp: str, separator: str, no_strip: bool, render: bool, render_path: str, repeat: int, mode: str, max_steps: int):
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
    for _ in range(repeat):
        res = model.run(Multiset(inp), render_steps=render, render_path=render_path, mode=mode, max_steps=max_steps)
        if mode == 'time-mc':
            print([dict(r) for r in res])
        elif mode == 'halt-mc':
            print(dict(res))
        else:
            print(res)


if __name__ == '__main__':
    main()
