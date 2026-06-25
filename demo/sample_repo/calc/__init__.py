"""calc — a tiny arithmetic expression evaluator.

Public surface: `calc(text)` parses and evaluates one expression string.
"""
from .cli import calc

__all__ = ["calc"]
__version__ = "0.1.0"
