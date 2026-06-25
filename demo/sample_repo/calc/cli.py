"""Command-line entry point: read an expression, print its value.

This is the top of the program. It wires the three stages together —
tokenize, parse, evaluate — and offers two modes: evaluate the expression
given on the command line, or read expressions line by line from stdin.
"""
from __future__ import annotations

import sys

from .evaluator import evaluate
from .parser import parse
from .tokens import tokenize


def calc(text: str) -> float:
    """Evaluate a single expression string end to end."""
    tokens = tokenize(text)
    tree = parse(tokens)
    return evaluate(tree)


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print(calc(" ".join(argv[1:])))
        return 0
    for line in sys.stdin:  # REPL mode: one expression per line
        line = line.strip()
        if not line:
            continue
        try:
            print(calc(line))
        except (SyntaxError, ZeroDivisionError, TypeError) as e:
            print(f"error: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
