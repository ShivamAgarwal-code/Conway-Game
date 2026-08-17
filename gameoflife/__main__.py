"""Command-line interface and terminal renderer for the Game of Life.

Examples
--------
Run the Gosper glider gun in an animated terminal view::

    python -m gameoflife --pattern gun --animate

Load a pattern from an RLE file and print 5 generations::

    python -m gameoflife --file mypattern.rle --steps 5

Start from a random soup on a 40x20 toroidal grid::

    python -m gameoflife --random 40x20 --wrap --animate
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from typing import List, Optional, Tuple

from .life import CONWAY, Life, Rule
from .patterns import PATTERNS, get_pattern
from .rle import parse_rle

Cell = Tuple[int, int]

_CLEAR = "\033[2J\033[H"  # ANSI: clear screen, move cursor home.


def _parse_dims(text: str) -> Tuple[int, int]:
    try:
        w, h = text.lower().split("x")
        return int(w), int(h)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Expected dimensions like '40x20', got {text!r}"
        )


def _random_cells(width: int, height: int, density: float, rng: random.Random) -> List[Cell]:
    return [
        (x, y)
        for y in range(height)
        for x in range(width)
        if rng.random() < density
    ]


def _center(cells: List[Cell], width: int, height: int) -> List[Cell]:
    """Shift a pattern so it sits roughly in the middle of a bounded grid."""
    if not cells:
        return cells
    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    pw = max(xs) - min(xs) + 1
    ph = max(ys) - min(ys) + 1
    ox = (width - pw) // 2 - min(xs)
    oy = (height - ph) // 2 - min(ys)
    return [(x + ox, y + oy) for x, y in cells]


def build_life(args: argparse.Namespace) -> Life:
    rule = Rule.parse(args.rule) if args.rule else CONWAY
    width = height = None
    wrap = args.wrap
    cells: List[Cell] = []

    if args.random:
        width, height = args.random
        rng = random.Random(args.seed)
        cells = _random_cells(width, height, args.density, rng)
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as fh:
            cells, file_rule = parse_rle(fh.read())
        if file_rule and not args.rule:
            rule = Rule.parse(file_rule)
    else:
        cells = get_pattern(args.pattern)

    if args.size:
        width, height = args.size
        cells = _center(cells, width, height)

    return Life(cells, rule=rule, width=width, height=height, wrap=wrap)


def _viewport(args: argparse.Namespace, life: Life) -> Optional[Tuple[int, int, int, int]]:
    if life.bounded:
        return (0, 0, life.width - 1, life.height - 1)
    if args.size:
        w, h = args.size
        return (0, 0, w - 1, h - 1)
    return None  # auto (bounding box)


def render(life: Life, box, alive: str, dead: str) -> str:
    grid = life.to_string(alive=alive, dead=dead, box=box)
    status = f"gen {life.generation}   pop {life.population}   rule {life.rule}"
    return f"{grid}\n{status}"


def run(args: argparse.Namespace) -> int:
    life = build_life(args)
    box = _viewport(args, life)

    if args.animate:
        try:
            for _ in range(args.steps + 1):
                sys.stdout.write(_CLEAR)
                sys.stdout.write(render(life, box, args.alive, args.dead))
                sys.stdout.write("\n")
                sys.stdout.flush()
                if life.population == 0:
                    break
                time.sleep(args.delay)
                life.step()
        except KeyboardInterrupt:
            print()
        return 0

    # Non-animated: print each requested generation separated by a blank line.
    frames = []
    for _ in range(args.steps + 1):
        frames.append(render(life, box, args.alive, args.dead))
        life.step()
    print("\n\n".join(frames))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gameoflife",
        description="Conway's Game of Life -- an infinite-grid cellular automaton.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "-p", "--pattern", default="glider",
        help=f"named starting pattern (default: glider). Available: {', '.join(PATTERNS)}",
    )
    source.add_argument("-f", "--file", help="load the starting pattern from an RLE file")
    source.add_argument(
        "-r", "--random", type=_parse_dims, metavar="WxH",
        help="start from a random soup on a WxH grid, e.g. 40x20",
    )

    parser.add_argument("-n", "--steps", type=int, default=20, help="number of generations (default: 20)")
    parser.add_argument("-a", "--animate", action="store_true", help="animate in the terminal")
    parser.add_argument("-d", "--delay", type=float, default=0.08, help="seconds between animated frames")
    parser.add_argument("--size", type=_parse_dims, metavar="WxH", help="bound the board to WxH and centre the pattern")
    parser.add_argument("--wrap", action="store_true", help="wrap edges (toroidal grid); requires --size or --random")
    parser.add_argument("--rule", help="rule string, e.g. B3/S23 (default) or B36/S23 (HighLife)")
    parser.add_argument("--density", type=float, default=0.3, help="live-cell probability for --random (default: 0.3)")
    parser.add_argument("--seed", type=int, help="random seed for --random")
    parser.add_argument("--alive", default="#", help="character for live cells (default: #)")
    parser.add_argument("--dead", default=".", help="character for dead cells (default: .)")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    sys.exit(main())
