# Conway's Game of Life

An implementation of [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) —
the classic zero-player cellular automaton devised by John Conway in 1970.

This repository contains two independent, dependency-free implementations that
share the same engine design:

- **Python package** (`gameoflife/`) — a sparse, effectively-infinite simulation
  engine with a terminal CLI, RLE/plaintext pattern loading, and a test suite.
- **Browser version** (`web/`) — an interactive HTML5 canvas you can click to
  draw on, with play/step controls, a pattern picker, and adjustable speed.

## The rules

The universe is an infinite grid of cells, each either **live** or **dead**.
Every generation, all cells update simultaneously according to the number of
their eight neighbours that are live (rule **B3/S23**):

| Current cell | Live neighbours | Next state |
| ------------ | --------------- | ---------- |
| Live         | 0 or 1          | Dies (underpopulation) |
| Live         | 2 or 3          | Survives   |
| Live         | 4 or more       | Dies (overpopulation)  |
| Dead         | exactly 3       | Born (reproduction)    |

From these simple rules an astonishing variety of behaviour emerges: still
lifes, oscillators, gliders and spaceships, and even patterns that grow forever.

## Design

The engine stores **only the live cells** as a set of `(x, y)` coordinates
rather than a dense 2-D array. Each generation it tallies neighbour counts only
for cells adjacent to a live cell — the only ones that can possibly change.
This makes memory and time proportional to the population, not the grid area, so
the board is effectively infinite and patterns like the Gosper glider gun can
run indefinitely without hitting a wall. A bounded, optionally toroidal
(wrap-around) grid is also supported.

## Python: quick start

No dependencies are required to run it (Python 3.8+):

```bash
# Animate the Gosper glider gun in your terminal (Ctrl-C to stop)
python -m gameoflife --pattern gun --animate

# Print 5 generations of a glider
python -m gameoflife --pattern glider --steps 5

# Random soup on a 50x25 wrap-around grid
python -m gameoflife --random 50x25 --wrap --animate

# Load a pattern from an RLE file
python -m gameoflife --file patterns/gosper_glider_gun.rle --animate
```

### Command-line options

| Option | Description |
| ------ | ----------- |
| `-p, --pattern NAME` | Named starting pattern (default: `glider`) |
| `-f, --file PATH`    | Load the starting pattern from an RLE file |
| `-r, --random WxH`   | Random soup on a `WxH` grid |
| `-n, --steps N`      | Number of generations (default: 20) |
| `-a, --animate`      | Animate in the terminal |
| `-d, --delay SECS`   | Delay between animated frames (default: 0.08) |
| `--size WxH`         | Bound the board to `WxH` and centre the pattern |
| `--wrap`             | Toroidal (wrap-around) edges |
| `--rule STR`         | Rule string, e.g. `B3/S23` (default) or `B36/S23` (HighLife) |
| `--density F`        | Live-cell probability for `--random` (default: 0.3) |
| `--seed N`           | Random seed for reproducible soups |
| `--alive / --dead`   | Glyphs used for live / dead cells |

Available named patterns: `acorn`, `beacon`, `beehive`, `blinker`, `block`,
`boat`, `diehard`, `glider`, `gosper_glider_gun` (alias `gun`), `loaf`, `lwss`,
`pulsar`, `r_pentomino`, `toad`, `tub`.

### Using the engine as a library

```python
from gameoflife import Life
from gameoflife.patterns import get_pattern

life = Life(get_pattern("glider"))
life.run(4)                 # advance 4 generations
print(life)                 # render live cells as text
print(life.population)      # 5
print(life.bounding_box())  # (1, 1, 3, 3) — the glider has moved
```

Custom rules and bounded grids:

```python
from gameoflife import Life, Rule

highlife = Rule.parse("B36/S23")
life = Life(width=40, height=20, wrap=True, rule=highlife)
life.set_alive(20, 10)
life.step()
```

## Browser version

Open `web/index.html` in any modern browser — no build step, no server needed.

- **Click or drag** on the grid to draw or erase cells.
- **Play / Pause / Step / Clear** controls, plus a **Random** soup generator.
- Load classic patterns (glider, pulsar, Gosper gun, …) from the dropdown.
- Adjust **speed** and **cell size**, and toggle **toroidal wrapping**.

It loads showing the Gosper glider gun already running.

## Running the tests

```bash
pip install -e ".[test]"
pytest -q
```

The suite (24 tests) covers still lifes, oscillator periods, glider translation,
infinite-grid negative coordinates, bounded and toroidal edge behaviour, custom
rules, and RLE/plaintext round-tripping. CI runs them on Python 3.8–3.13.

## Repository layout

```
gameoflife/        Python package
  life.py          sparse simulation engine + Rule
  patterns.py      classic pattern library + plaintext parser
  rle.py           Run Length Encoded format reader/writer
  __main__.py      command-line interface & terminal renderer
web/               interactive browser version (HTML + JS canvas)
patterns/          sample .rle pattern files
tests/             pytest suite
```

## License

Released under the MIT License — see [LICENSE](LICENSE).
