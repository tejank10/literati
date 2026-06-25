"""Enables `python -m calc "<expression>"`."""
import sys

from .cli import main

raise SystemExit(main(sys.argv))
