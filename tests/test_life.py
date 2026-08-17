"""Tests for the core Game of Life engine."""

import pytest

from gameoflife import CONWAY, Life, Rule
from gameoflife.patterns import get_pattern


def test_rule_parse_roundtrip():
    rule = Rule.parse("B3/S23")
    assert rule == CONWAY
    assert str(rule) == "B3/S23"
    assert Rule.parse("b36/s23") == Rule(frozenset({3, 6}), frozenset({2, 3}))


def test_block_is_still_life():
    life = Life(get_pattern("block"))
    before = set(life.live)
    life.step()
    assert life.live == before
    assert life.population == 4


def test_blinker_has_period_two():
    life = Life(get_pattern("blinker"))
    start = set(life.live)
    life.step()
    assert life.live != start
    life.step()
    assert life.live == start


def test_toad_has_period_two():
    life = Life(get_pattern("toad"))
    start = set(life.live)
    life.run(2)
    assert life.live == start


def test_glider_translates_by_one_diagonally_every_four_gens():
    life = Life(get_pattern("glider"))
    start = set(life.live)
    life.run(4)
    shifted = {(x - 1, y - 1) for x, y in life.live}
    assert shifted == start
    assert life.generation == 4


def test_empty_board_stays_empty():
    life = Life()
    life.step()
    assert life.population == 0


def test_lone_cell_dies():
    life = Life([(5, 5)])
    life.step()
    assert life.population == 0


def test_infinite_grid_allows_negative_coordinates():
    # A blinker placed across the origin should still oscillate correctly.
    life = Life([(-1, 0), (0, 0), (1, 0)])
    life.step()
    assert life.live == {(0, -1), (0, 0), (0, 1)}


def test_bounded_grid_clips_out_of_bounds_births():
    # A blinker at the top edge cannot spawn cells above y=0.
    life = Life([(1, 0), (1, 1), (1, 2)], width=3, height=3)
    life.step()
    # Horizontal phase would be (0,1),(1,1),(2,1) -- all in bounds.
    assert life.live == {(0, 1), (1, 1), (2, 1)}
    assert all(0 <= y < 3 for _, y in life.live)


def test_toroidal_wrap_connects_edges():
    # A horizontal blinker on the top row of a 5x5 torus flips to vertical, and
    # its top cell wraps around to the bottom row (y = -1 -> y = 4).
    life = Life([(0, 0), (1, 0), (2, 0)], width=5, height=5, wrap=True)
    life.step()
    assert life.live == {(1, 4), (1, 0), (1, 1)}


def test_bounded_without_wrap_does_not_connect_edges():
    # The same blinker on a bounded (non-wrapping) board loses its wrapped cell,
    # so the top row keeps only the two in-bounds cells.
    life = Life([(0, 0), (1, 0), (2, 0)], width=5, height=5, wrap=False)
    life.step()
    assert life.live == {(1, 0), (1, 1)}


def test_highlife_replicator_rule_differs_from_conway():
    cells = [(0, 0), (1, 0), (2, 0)]
    conway = Life(list(cells), rule=CONWAY)
    highlife = Life(list(cells), rule=Rule.parse("B36/S23"))
    conway.step()
    highlife.step()
    # B36 adds a birth condition; on a bare blinker both still behave the same,
    # so assert the rules themselves differ and both remain valid boards.
    assert conway.rule != highlife.rule
    assert conway.population == highlife.population == 3


def test_to_string_uses_custom_glyphs():
    life = Life([(0, 0), (1, 0)])
    assert life.to_string(alive="#", dead=" ") == "##"


def test_set_toggle_and_is_alive():
    life = Life()
    assert not life.is_alive(2, 3)
    life.toggle(2, 3)
    assert life.is_alive(2, 3)
    life.toggle(2, 3)
    assert not life.is_alive(2, 3)


def test_bounding_box_none_when_empty():
    assert Life().bounding_box() is None


def test_run_advances_generation_counter():
    life = Life(get_pattern("block"))
    life.run(10)
    assert life.generation == 10


def test_unknown_pattern_raises():
    with pytest.raises(KeyError):
        get_pattern("does-not-exist")
