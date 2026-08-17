"""Core simulation engine for Conway's Game of Life.

The engine stores only *live* cells as a set of ``(x, y)`` coordinates. This
keeps memory proportional to the number of live cells rather than the size of
the grid, so the default board is effectively infinite -- patterns such as
glider guns can run forever without hitting a wall.

A bounded, optionally toroidal (wrap-around) grid is also supported for cases
where a fixed playfield is desired.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Iterator, Optional, Set, Tuple

Cell = Tuple[int, int]

# The eight neighbours surrounding a cell (Moore neighbourhood).
_NEIGHBOUR_OFFSETS: Tuple[Cell, ...] = (
    (-1, -1), (0, -1), (1, -1),
    (-1, 0), (1, 0),
    (-1, 1), (0, 1), (1, 1),
)


@dataclass(frozen=True)
class Rule:
    """A totalistic birth/survival rule.

    ``birth`` is the set of neighbour counts that bring a dead cell to life.
    ``survival`` is the set of neighbour counts that keep a live cell alive.
    Conway's Game of Life is ``B3/S23``.
    """

    birth: frozenset
    survival: frozenset

    @classmethod
    def parse(cls, text: str) -> "Rule":
        """Parse a rule string such as ``"B3/S23"`` (case-insensitive)."""
        parts = text.upper().replace(" ", "").split("/")
        birth: Set[int] = set()
        survival: Set[int] = set()
        for part in parts:
            if not part:
                continue
            kind, digits = part[0], part[1:]
            counts = {int(d) for d in digits if d.isdigit()}
            if kind == "B":
                birth = counts
            elif kind == "S":
                survival = counts
            else:
                raise ValueError(f"Unrecognised rule segment: {part!r}")
        return cls(frozenset(birth), frozenset(survival))

    def __str__(self) -> str:
        b = "".join(str(n) for n in sorted(self.birth))
        s = "".join(str(n) for n in sorted(self.survival))
        return f"B{b}/S{s}"


# The classic Conway rule.
CONWAY = Rule(frozenset({3}), frozenset({2, 3}))


class Life:
    """A Game of Life board.

    Live cells are held as a ``set`` of integer ``(x, y)`` coordinates. When
    ``width`` and ``height`` are given the board is bounded to
    ``0 <= x < width`` and ``0 <= y < height``; with ``wrap=True`` the edges
    connect to form a torus. Without dimensions the board is unbounded.
    """

    def __init__(
        self,
        cells: Optional[Iterable[Cell]] = None,
        rule: Rule = CONWAY,
        width: Optional[int] = None,
        height: Optional[int] = None,
        wrap: bool = False,
    ) -> None:
        self.rule = rule
        self.width = width
        self.height = height
        self.wrap = wrap
        self.generation = 0
        self.live: Set[Cell] = set()
        if cells:
            for cell in cells:
                self.live.add(self._normalise(cell))

    # -- geometry ---------------------------------------------------------
    @property
    def bounded(self) -> bool:
        return self.width is not None and self.height is not None

    def _normalise(self, cell: Cell) -> Cell:
        """Apply wrap-around, or drop out-of-bounds cells on a bounded board."""
        x, y = cell
        if not self.bounded:
            return (x, y)
        if self.wrap:
            return (x % self.width, y % self.height)
        return (x, y)

    def _in_bounds(self, cell: Cell) -> bool:
        if not self.bounded:
            return True
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height

    def _neighbours(self, cell: Cell) -> Iterator[Cell]:
        x, y = cell
        for dx, dy in _NEIGHBOUR_OFFSETS:
            nx, ny = x + dx, y + dy
            if self.bounded and self.wrap:
                nx %= self.width
                ny %= self.height
            yield (nx, ny)

    # -- state ------------------------------------------------------------
    def is_alive(self, x: int, y: int) -> bool:
        return self._normalise((x, y)) in self.live

    def set_alive(self, x: int, y: int, alive: bool = True) -> None:
        cell = self._normalise((x, y))
        if self.bounded and not self.wrap and not self._in_bounds(cell):
            return
        if alive:
            self.live.add(cell)
        else:
            self.live.discard(cell)

    def toggle(self, x: int, y: int) -> None:
        self.set_alive(x, y, not self.is_alive(x, y))

    @property
    def population(self) -> int:
        return len(self.live)

    def bounding_box(self) -> Optional[Tuple[int, int, int, int]]:
        """Return ``(min_x, min_y, max_x, max_y)`` of live cells, or ``None``."""
        if not self.live:
            return None
        xs = [x for x, _ in self.live]
        ys = [y for _, y in self.live]
        return (min(xs), min(ys), max(xs), max(ys))

    # -- evolution --------------------------------------------------------
    def step(self) -> "Life":
        """Advance the board by one generation, in place. Returns ``self``."""
        # Count live neighbours for every cell adjacent to a live cell. Only
        # those cells can possibly be alive next generation, which is what makes
        # the sparse approach efficient.
        neighbour_counts: Counter = Counter()
        for cell in self.live:
            for neighbour in self._neighbours(cell):
                neighbour_counts[neighbour] += 1

        birth, survival = self.rule.birth, self.rule.survival
        next_live: Set[Cell] = set()
        for cell, count in neighbour_counts.items():
            if not self._in_bounds(cell):
                continue
            if cell in self.live:
                if count in survival:
                    next_live.add(cell)
            elif count in birth:
                next_live.add(cell)

        self.live = next_live
        self.generation += 1
        return self

    def run(self, generations: int) -> "Life":
        """Advance the board by ``generations`` steps."""
        for _ in range(generations):
            self.step()
        return self

    # -- rendering --------------------------------------------------------
    def to_string(
        self,
        alive: str = "O",
        dead: str = ".",
        box: Optional[Tuple[int, int, int, int]] = None,
    ) -> str:
        """Render the board as text.

        ``box`` fixes the viewport as ``(min_x, min_y, max_x, max_y)``; without
        it the live-cell bounding box is used (a blank board renders empty).
        """
        if box is None:
            if self.bounded:
                box = (0, 0, self.width - 1, self.height - 1)
            else:
                box = self.bounding_box()
        if box is None:
            return ""
        min_x, min_y, max_x, max_y = box
        rows = []
        for y in range(min_y, max_y + 1):
            rows.append(
                "".join(
                    alive if (x, y) in self.live else dead
                    for x in range(min_x, max_x + 1)
                )
            )
        return "\n".join(rows)

    def __str__(self) -> str:
        return self.to_string()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Life):
            return NotImplemented
        return self.live == other.live and self.rule == other.rule

    def __repr__(self) -> str:
        dims = f", {self.width}x{self.height}" if self.bounded else ""
        return (
            f"Life(population={self.population}, generation={self.generation}, "
            f"rule={self.rule}{dims})"
        )
