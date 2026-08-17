"use strict";

/**
 * Conway's Game of Life engine (browser build).
 *
 * Mirrors the Python engine: live cells are stored sparsely in a Set keyed by
 * "x,y" strings, so the board is effectively unbounded. A bounded, optionally
 * toroidal grid is supported by passing width/height and wrap.
 */
class Life {
  constructor({ width = null, height = null, wrap = false } = {}) {
    this.width = width;
    this.height = height;
    this.wrap = wrap;
    this.generation = 0;
    this.live = new Set(); // keys: "x,y"
  }

  get bounded() {
    return this.width !== null && this.height !== null;
  }

  get population() {
    return this.live.size;
  }

  static key(x, y) {
    return x + "," + y;
  }

  _norm(x, y) {
    if (this.bounded && this.wrap) {
      x = ((x % this.width) + this.width) % this.width;
      y = ((y % this.height) + this.height) % this.height;
    }
    return [x, y];
  }

  _inBounds(x, y) {
    if (!this.bounded) return true;
    return x >= 0 && x < this.width && y >= 0 && y < this.height;
  }

  isAlive(x, y) {
    const [nx, ny] = this._norm(x, y);
    return this.live.has(Life.key(nx, ny));
  }

  setAlive(x, y, alive = true) {
    const [nx, ny] = this._norm(x, y);
    if (this.bounded && !this.wrap && !this._inBounds(nx, ny)) return;
    const k = Life.key(nx, ny);
    if (alive) this.live.add(k);
    else this.live.delete(k);
  }

  toggle(x, y) {
    this.setAlive(x, y, !this.isAlive(x, y));
  }

  clear() {
    this.live.clear();
    this.generation = 0;
  }

  step() {
    const counts = new Map();
    const bump = (x, y) => {
      const k = Life.key(x, y);
      counts.set(k, (counts.get(k) || 0) + 1);
    };
    for (const cell of this.live) {
      const [cx, cy] = cell.split(",").map(Number);
      for (let dy = -1; dy <= 1; dy++) {
        for (let dx = -1; dx <= 1; dx++) {
          if (dx === 0 && dy === 0) continue;
          let nx = cx + dx;
          let ny = cy + dy;
          if (this.bounded && this.wrap) {
            nx = ((nx % this.width) + this.width) % this.width;
            ny = ((ny % this.height) + this.height) % this.height;
          }
          bump(nx, ny);
        }
      }
    }

    const next = new Set();
    for (const [k, n] of counts) {
      const [x, y] = k.split(",").map(Number);
      if (this.bounded && !this._inBounds(x, y)) continue;
      const alive = this.live.has(k);
      if (alive ? n === 2 || n === 3 : n === 3) next.add(k);
    }
    this.live = next;
    this.generation++;
  }

  /** Load an array of [x, y] cells, offset by (ox, oy). */
  load(cells, ox = 0, oy = 0) {
    for (const [x, y] of cells) this.setAlive(x + ox, y + oy);
  }
}

/** Classic patterns as arrays of [x, y] live-cell coordinates. */
const PATTERNS = {
  glider: [[1, 0], [2, 1], [0, 2], [1, 2], [2, 2]],
  lwss: [[1, 0], [4, 0], [0, 1], [0, 2], [4, 2], [0, 3], [1, 3], [2, 3], [3, 3]],
  blinker: [[0, 0], [1, 0], [2, 0]],
  toad: [[1, 0], [2, 0], [3, 0], [0, 1], [1, 1], [2, 1]],
  beacon: [[0, 0], [1, 0], [0, 1], [1, 1], [2, 2], [3, 2], [2, 3], [3, 3]],
  rpentomino: [[1, 0], [2, 0], [0, 1], [1, 1], [1, 2]],
  acorn: [[1, 0], [3, 1], [0, 2], [1, 2], [4, 2], [5, 2], [6, 2]],
  diehard: [[6, 0], [0, 1], [1, 1], [1, 2], [5, 2], [6, 2], [7, 2]],
  pulsar: parseAscii([
    "..OOO...OOO..",
    ".............",
    "O....O.O....O",
    "O....O.O....O",
    "O....O.O....O",
    "..OOO...OOO..",
    ".............",
    "..OOO...OOO..",
    "O....O.O....O",
    "O....O.O....O",
    "O....O.O....O",
    ".............",
    "..OOO...OOO..",
  ]),
  gun: parseAscii([
    "........................O...........",
    "......................O.O...........",
    "............OO......OO............OO",
    "...........O...O....OO............OO",
    "OO........O.....O...OO..............",
    "OO........O...O.OO....O.O...........",
    "..........O.....O.......O...........",
    "...........O...O....................",
    "............OO......................",
  ]),
};

function parseAscii(rows) {
  const cells = [];
  rows.forEach((row, y) => {
    for (let x = 0; x < row.length; x++) {
      if (row[x] === "O") cells.push([x, y]);
    }
  });
  return cells;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { Life, PATTERNS };
}
