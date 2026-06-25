"""Tree-walk evaluator: an AST becomes a number.

Because the parser already encoded precedence in the tree's shape, evaluation
is a straightforward post-order walk: evaluate the children, then combine them.
"""
from __future__ import annotations

from .nodes import BinOp, Node, Num, Unary


def evaluate(node: Node) -> float:
    if isinstance(node, Num):
        return node.value
    if isinstance(node, Unary):
        return -evaluate(node.operand)
    if isinstance(node, BinOp):
        left = evaluate(node.left)
        right = evaluate(node.right)
        if node.op == "+":
            return left + right
        if node.op == "-":
            return left - right
        if node.op == "*":
            return left * right
        if node.op == "/":
            return left / right
    raise TypeError(f"cannot evaluate node {node!r}")
