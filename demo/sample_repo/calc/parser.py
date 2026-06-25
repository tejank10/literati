"""Recursive-descent parser: a token list becomes an AST.

Precedence and associativity are expressed by the grammar's layering rather
than by a table:

    expression := term   (('+' | '-') term)*       # lowest precedence
    term       := factor (('*' | '/') factor)*      # binds tighter
    factor     := NUMBER | '(' expression ')' | '-' factor   # tightest

Each rule is one method. Left-associativity falls out of the `while` loops:
operators found later are attached as the *right* child of a node built from
everything seen so far.
"""
from __future__ import annotations

from .nodes import BinOp, Node, Num, Unary
from .tokens import EOF, LPAREN, MINUS, NUMBER, PLUS, RPAREN, SLASH, STAR, Token


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, kind: str) -> Token:
        if self.peek().kind != kind:
            raise SyntaxError(f"expected {kind}, got {self.peek().kind}")
        return self.advance()

    def parse(self) -> Node:
        node = self.expression()
        self.expect(EOF)  # nothing may follow a complete expression
        return node

    def expression(self) -> Node:
        node = self.term()
        while self.peek().kind in (PLUS, MINUS):
            op = self.advance().value
            node = BinOp(op, node, self.term())
        return node

    def term(self) -> Node:
        node = self.factor()
        while self.peek().kind in (STAR, SLASH):
            op = self.advance().value
            node = BinOp(op, node, self.factor())
        return node

    def factor(self) -> Node:
        tok = self.peek()
        if tok.kind == NUMBER:
            self.advance()
            return Num(float(tok.value))
        if tok.kind == LPAREN:
            self.advance()
            node = self.expression()
            self.expect(RPAREN)
            return node
        if tok.kind == MINUS:
            self.advance()
            return Unary("-", self.factor())
        raise SyntaxError(f"unexpected token {tok.kind}")


def parse(tokens: list[Token]) -> Node:
    return Parser(tokens).parse()
