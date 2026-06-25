"""Token kinds and the tokenizer for the calc expression language.

The tokenizer turns a flat string like "1 + 2 * 3" into a list of Tokens,
discarding whitespace and rejecting characters the language does not allow.
It is deliberately dumb: it knows nothing about precedence or grouping.
"""
from __future__ import annotations

from dataclasses import dataclass

# Token kinds (used as opaque tags by the parser).
NUMBER = "NUMBER"
PLUS = "PLUS"
MINUS = "MINUS"
STAR = "STAR"
SLASH = "SLASH"
LPAREN = "LPAREN"
RPAREN = "RPAREN"
EOF = "EOF"

# Single-character operators and punctuation map straight to a kind.
_SINGLE = {
    "+": PLUS,
    "-": MINUS,
    "*": STAR,
    "/": SLASH,
    "(": LPAREN,
    ")": RPAREN,
}


@dataclass
class Token:
    kind: str
    value: str


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
            continue
        if c in _SINGLE:
            tokens.append(Token(_SINGLE[c], c))
            i += 1
            continue
        if c.isdigit() or c == ".":
            start = i
            while i < n and (text[i].isdigit() or text[i] == "."):
                i += 1
            tokens.append(Token(NUMBER, text[start:i]))
            continue
        raise SyntaxError(f"unexpected character {c!r} at position {i}")
    tokens.append(Token(EOF, ""))
    return tokens
