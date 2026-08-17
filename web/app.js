"use strict";

/* UI controller for the browser Game of Life. Handles the canvas grid, mouse
 * painting, the animation loop, and the control panel. */

(function () {
  const canvas = document.getElementById("board");
  const ctx = canvas.getContext("2d");

  const els = {
    play: document.getElementById("playBtn"),
    step: document.getElementById("stepBtn"),
    clear: document.getElementById("clearBtn"),
    random: document.getElementById("randomBtn"),
    pattern: document.getElementById("pattern"),
    speed: document.getElementById("speed"),
    speedVal: document.getElementById("speedVal"),
    cellSize: document.getElementById("cellSize"),
    cellVal: document.getElementById("cellVal"),
    wrap: document.getElementById("wrap"),
    gen: document.getElementById("genStat"),
    pop: document.getElementById("popStat"),
  };

  let cell = parseInt(els.cellSize.value, 10);
  let cols = 0;
  let rows = 0;
  let life = new Life();
  let running = false;
  let lastTick = 0;
  let fps = parseInt(els.speed.value, 10);

  const COLORS = {
    bg: "#161b22",
    grid: "#21262d",
    cell: "#3fb950",
  };

  function resize() {
    const wrap = canvas.parentElement;
    const cssWidth = wrap.clientWidth;
    const cssHeight = Math.max(360, Math.round(window.innerHeight * 0.7));
    const dpr = window.devicePixelRatio || 1;
    canvas.width = cssWidth * dpr;
    canvas.height = cssHeight * dpr;
    canvas.style.height = cssHeight + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    cols = Math.floor(cssWidth / cell);
    rows = Math.floor(cssHeight / cell);
    life.width = cols;
    life.height = rows;
    life.wrap = els.wrap.checked;
    draw();
  }

  function draw() {
    const w = cols * cell;
    const h = rows * cell;
    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Grid lines.
    ctx.strokeStyle = COLORS.grid;
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = 0; x <= cols; x++) {
      ctx.moveTo(x * cell + 0.5, 0);
      ctx.lineTo(x * cell + 0.5, h);
    }
    for (let y = 0; y <= rows; y++) {
      ctx.moveTo(0, y * cell + 0.5);
      ctx.lineTo(w, y * cell + 0.5);
    }
    ctx.stroke();

    // Live cells.
    ctx.fillStyle = COLORS.cell;
    for (const k of life.live) {
      const [x, y] = k.split(",").map(Number);
      ctx.fillRect(x * cell + 1, y * cell + 1, cell - 1, cell - 1);
    }

    els.gen.textContent = life.generation;
    els.pop.textContent = life.population;
  }

  function loop(now) {
    if (!running) return;
    const interval = 1000 / fps;
    if (now - lastTick >= interval) {
      life.step();
      draw();
      lastTick = now;
    }
    requestAnimationFrame(loop);
  }

  function setRunning(on) {
    running = on;
    els.play.textContent = on ? "⏸ Pause" : "▶ Play";
    els.play.classList.toggle("primary", !on);
    if (on) {
      lastTick = 0;
      requestAnimationFrame(loop);
    }
  }

  // -- pointer painting ------------------------------------------------
  let painting = false;
  let paintValue = true;

  function cellAt(evt) {
    const rect = canvas.getBoundingClientRect();
    const px = (evt.clientX - rect.left);
    const py = (evt.clientY - rect.top);
    return [Math.floor(px / cell), Math.floor(py / cell)];
  }

  canvas.addEventListener("pointerdown", (e) => {
    e.preventDefault();
    const [x, y] = cellAt(e);
    paintValue = !life.isAlive(x, y);
    life.setAlive(x, y, paintValue);
    painting = true;
    canvas.setPointerCapture(e.pointerId);
    draw();
  });
  canvas.addEventListener("pointermove", (e) => {
    if (!painting) return;
    const [x, y] = cellAt(e);
    life.setAlive(x, y, paintValue);
    draw();
  });
  const stopPaint = () => (painting = false);
  canvas.addEventListener("pointerup", stopPaint);
  canvas.addEventListener("pointercancel", stopPaint);

  // -- controls --------------------------------------------------------
  els.play.addEventListener("click", () => setRunning(!running));
  els.step.addEventListener("click", () => {
    setRunning(false);
    life.step();
    draw();
  });
  els.clear.addEventListener("click", () => {
    setRunning(false);
    life.clear();
    draw();
  });
  els.random.addEventListener("click", () => {
    life.clear();
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        if (Math.random() < 0.28) life.setAlive(x, y);
      }
    }
    draw();
  });
  els.pattern.addEventListener("change", () => {
    const name = els.pattern.value;
    if (!name || !PATTERNS[name]) return;
    setRunning(false);
    life.clear();
    const cells = PATTERNS[name];
    const pw = Math.max(...cells.map((c) => c[0])) + 1;
    const ph = Math.max(...cells.map((c) => c[1])) + 1;
    const ox = Math.floor((cols - pw) / 2);
    const oy = Math.floor((rows - ph) / 2);
    life.load(cells, ox, oy);
    draw();
    els.pattern.value = "";
  });
  els.speed.addEventListener("input", () => {
    fps = parseInt(els.speed.value, 10);
    els.speedVal.textContent = fps;
  });
  els.cellSize.addEventListener("input", () => {
    cell = parseInt(els.cellSize.value, 10);
    els.cellVal.textContent = cell;
    resize();
  });
  els.wrap.addEventListener("change", () => {
    life.wrap = els.wrap.checked;
  });

  window.addEventListener("resize", resize);

  // Start with a gentle demo: the Gosper glider gun.
  resize();
  const gun = PATTERNS.gun;
  life.load(gun, 2, 2);
  draw();
})();
