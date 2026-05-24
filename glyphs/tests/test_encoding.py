"""Tests for bitmap digit encoding."""

from __future__ import annotations

import pytest

from glyphs.encoding import digit_from_glyph, glyph_for_digit, placements_from_digit
from glyphs.placement import Placement
from glyphs.scheme import Scheme


def test_digit_12_placements() -> None:
    arms = placements_from_digit(12)
    assert arms == frozenset({Placement.BIT_2, Placement.BIT_3})


def test_glyph_for_digit_12_round_trip() -> None:
    glyph = glyph_for_digit(Scheme.S60, 12)
    assert digit_from_glyph(glyph) == 12
    assert glyph.arms == frozenset({Placement.BIT_2, Placement.BIT_3})


@pytest.mark.parametrize("digit", range(60))
def test_s60_round_trip(digit: int) -> None:
    glyph = glyph_for_digit(Scheme.S60, digit)
    assert digit_from_glyph(glyph) == digit


@pytest.mark.parametrize("digit", range(64))
def test_s64_round_trip(digit: int) -> None:
    glyph = glyph_for_digit(Scheme.S64, digit)
    assert digit_from_glyph(glyph) == digit


@pytest.mark.parametrize("digit", [60, 61, 62, 63])
def test_s60_forbidden_digits(digit: int) -> None:
    with pytest.raises(ValueError, match="out of range"):
        glyph_for_digit(Scheme.S60, digit)


def test_s64_rejects_64() -> None:
    with pytest.raises(ValueError, match="out of range"):
        glyph_for_digit(Scheme.S64, 64)
