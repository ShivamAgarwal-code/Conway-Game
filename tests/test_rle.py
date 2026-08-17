"""Tests for RLE and plaintext pattern parsing."""

from gameoflife.patterns import PATTERNS, get_pattern, parse_cells
from gameoflife.rle import parse_rle, to_rle


def test_parse_cells_reads_live_coordinates():
    cells = parse_cells("O.O\n.O.")
    assert set(cells) == {(0, 0), (2, 0), (1, 1)}


def test_parse_cells_skips_comment_lines():
    cells = parse_cells("!name: thing\nOO")
    assert set(cells) == {(0, 0), (1, 0)}


def test_parse_rle_glider():
    cells, rule = parse_rle("x = 3, y = 3, rule = B3/S23\nbob$2bo$3o!")
    assert set(cells) == {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}
    assert rule == "B3/S23"


def test_parse_rle_handles_run_counts_and_blank_rows():
    cells, _ = parse_rle("x = 4, y = 3, rule = B3/S23\n4o2$2o!")
    assert set(cells) == {(0, 0), (1, 0), (2, 0), (3, 0), (0, 2), (1, 2)}


def test_parse_rle_ignores_hash_comments():
    text = "#N Glider\n#C A comment\nx = 3, y = 3\nbo$2bo$3o!"
    cells, _ = parse_rle(text)
    assert (1, 0) in cells


def test_to_rle_roundtrips_all_named_patterns():
    for name in PATTERNS:
        cells = get_pattern(name)
        encoded = to_rle(cells)
        decoded, _ = parse_rle(encoded)
        # RLE is translation-normalised to the origin, so compare shapes
        # after shifting both to their own bounding-box origin.
        assert _normalise(decoded) == _normalise(cells), name


def test_to_rle_empty():
    assert to_rle([]).endswith("!")


def _normalise(cells):
    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    ox, oy = min(xs), min(ys)
    return {(x - ox, y - oy) for x, y in cells}
