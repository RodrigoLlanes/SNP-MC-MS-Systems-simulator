import sys


def error(label: str, error_type: str, msg: str, code: int = 1, kill: bool = True):
    print(f'{error_type} ({label}): {msg}', file=sys.stderr)
    if kill:
        sys.exit(code)
