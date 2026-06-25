"""Abstract syntax tree node types for calc.

Three node kinds are enough for arithmetic: a literal number, a binary
operation, and a unary negation. The tree's *shape* encodes precedence and
associativity, so the evaluator never has to think about either.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass
class Num:
    value: float


@dataclass
class BinOp:
    op: str  # one of: + - * /
    left: "Node"
    right: "Node"


@dataclass
class Unary:
    op: str  # currently only '-'
    operand: "Node"


Node = Union[Num, BinOp, Unary]
