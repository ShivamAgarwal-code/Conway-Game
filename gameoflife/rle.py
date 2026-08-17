"""Reading and writing the Run Length Encoded (RLE) pattern format.

RLE is the de-facto standard for sharing Game of Life patterns. See
https://conwaylife.com/wiki/Run_Length_Encoded for the full specification.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

Cell = Tuple[int, int]

_HEADER_RE = re.compile(
    r"x\s*=\s*(\d+)\s*,\s*y\s*=\s*(\d+)\s*(?:,\s*rule\s*=\s*(\S+))?",
    re.IGNORECASE,
)


def parse_rle(text: str) -> Tuple[List[Cell], Optional[str]]:
    """Parse an RLE document.

    Returns ``(cells, rule)`` where ``cells`` is a list of live ``(x, y)``
    coordinates and ``rule`` is the rule string from the header, or ``None``.
    Comment (``#``) lines and the header line are handled per the spec.
    """
    rule: Optional[str] = None
    body_lines: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        header = _HEADER_RE.match(stripped)
        if header:
            rule = header.group(3)
            continue
        body_lines.append(stripped)

    body = "".join(body_lines)
    cells: List[Cell] = []
    x = y = 0
    count = 0
    for ch in body:
        if ch.isdigit():
            count = count * 10 + int(ch)
            continue
        run = count or 1
        count = 0
        if ch == "b":  # dead cells
            x += run
        elif ch == "o":  # live cells
            for _ in range(run):
                cells.append((x, y))
                x += 1
        elif ch == "$":  # end of row(s)
            y += run
            x = 0
        elif ch == "!":  # end of pattern
            break
        # Any other character (e.g. whitespace) is ignored.
    return cells, rule


def to_rle(cells: List[Cell], rule: str = "B3/S23") -> str:
    """Encode a list of live cells as an RLE document."""
    if not cells:
        return f"x = 0, y = 0, rule = {rule}\n!"
    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    min_x, min_y = min(xs), min(ys)
    width = max(xs) - min_x + 1
    height = max(ys) - min_y + 1
    live = {(x - min_x, y - min_y) for x, y in cells}

    # Build a run-length token stream row by row.
    tokens: List[str] = []
    for y in range(height):
        row: List[Tuple[str, int]] = []
        for x in range(width):
            tag = "o" if (x, y) in live else "b"
            if row and row[-1][0] == tag:
                row[-1] = (tag, row[-1][1] + 1)
            else:
                row.append((tag, 1))
        # Trim trailing dead cells; they are implied by the row break.
        while row and row[-1][0] == "b":
            row.pop()
        for tag, n in row:
            tokens.append(f"{n if n > 1 else ''}{tag}")
        if y < height - 1:
            tokens.append("$")
    tokens.append("!")

    header = f"x = {width}, y = {height}, rule = {rule}"
    return header + "\n" + _wrap("".join(tokens))


def _wrap(text: str, width: int = 70) -> str:
    """Wrap the encoded stream to ``width`` columns, as RLE files do."""
    lines = [text[i : i + width] for i in range(0, len(text), width)]
    return "\n".join(lines)
