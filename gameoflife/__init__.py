"""Conway's Game of Life.

A clean, dependency-free implementation of Conway's Game of Life featuring a
sparse-set simulation engine that supports an effectively infinite grid as well
as a bounded/toroidal grid, a terminal renderer, and RLE/plaintext pattern
loading.
"""

from .life import Life, Rule, CONWAY
from .patterns import PATTERNS, get_pattern

__all__ = ["Life", "Rule", "CONWAY", "PATTERNS", "get_pattern"]
__version__ = "1.0.0"
