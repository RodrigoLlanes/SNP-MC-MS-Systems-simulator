import sys


def error(label: str, error_type: str, msg: str, code: int = 1, kill: bool = True):
    raise AssertionError(f'{error_type} ({label}): {msg}')
