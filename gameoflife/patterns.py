"""A small library of classic Game of Life patterns.

Patterns are stored in the plaintext cells format (``.`` = dead, ``O`` = live)
and parsed on demand into coordinate lists. Names are case-insensitive.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

Cell = Tuple[int, int]


def parse_cells(text: str, alive: str = "O") -> List[Cell]:
    """Parse a plaintext-cells grid into a list of live ``(x, y)`` coords.

    Any character in ``alive`` (default ``"O"``) marks a live cell; ``!`` lines
    are treated as comments and skipped, matching the common ``.cells`` format.
    """
    cells: List[Cell] = []
    y = 0
    for line in text.splitlines():
        if line.startswith("!"):
            continue
        for x, ch in enumerate(line):
            if ch in alive:
                cells.append((x, y))
        y += 1
    return cells


# Raw plaintext patterns keyed by canonical name.
_RAW: Dict[str, str] = {
    "block": "OO\nOO",
    "beehive": ".OO.\nO..O\n.OO.",
    "loaf": ".OO.\nO..O\n.O.O\n..O.",
    "boat": "OO.\nO.O\n.O.",
    "tub": ".O.\nO.O\n.O.",
    "blinker": "OOO",
    "toad": ".OOO\nOOO.",
    "beacon": "OO..\nOO..\n..OO\n..OO",
    "pulsar": (
        "..OOO...OOO..\n"
        ".............\n"
        "O....O.O....O\n"
        "O....O.O....O\n"
        "O....O.O....O\n"
        "..OOO...OOO..\n"
        ".............\n"
        "..OOO...OOO..\n"
        "O....O.O....O\n"
        "O....O.O....O\n"
        "O....O.O....O\n"
        ".............\n"
        "..OOO...OOO.."
    ),
    "glider": ".O.\n..O\nOOO",
    "lwss": ".O..O\nO....\nO...O\nOOOO.",
    "gosper_glider_gun": (
        "........................O...........\n"
        "......................O.O...........\n"
        "............OO......OO............OO\n"
        "...........O...O....OO............OO\n"
        "OO........O.....O...OO..............\n"
        "OO........O...O.OO....O.O...........\n"
        "..........O.....O.......O...........\n"
        "...........O...O....................\n"
        "............OO......................"
    ),
    "r_pentomino": ".OO\nOO.\n.O.",
    "diehard": "......O.\nOO......\n.O...OOO",
    "acorn": ".O.....\n...O...\nOO..OOO",
}

# Friendly aliases.
_ALIASES: Dict[str, str] = {
    "gun": "gosper_glider_gun",
    "gospergun": "gosper_glider_gun",
    "glidergun": "gosper_glider_gun",
    "lightweight_spaceship": "lwss",
    "spaceship": "lwss",
    "rpentomino": "r_pentomino",
}

PATTERNS: Tuple[str, ...] = tuple(sorted(_RAW))


def _canonical(name: str) -> str:
    key = name.strip().lower().replace("-", "_").replace(" ", "_")
    key = _ALIASES.get(key.replace("_", ""), _ALIASES.get(key, key))
    return key


def get_pattern(name: str) -> List[Cell]:
    """Return the live cells for a named pattern.

    Raises ``KeyError`` with the list of known names if ``name`` is unknown.
    """
    key = _canonical(name)
    if key not in _RAW:
        raise KeyError(
            f"Unknown pattern {name!r}. Available: {', '.join(PATTERNS)}"
        )
    return parse_cells(_RAW[key])
