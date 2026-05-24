"""Tests for glyph composition."""

from __future__ import annotations

from glyphs.encoding import glyph_for_digit
from glyphs.scheme import Scheme
from glyphs.stroke import glyph_strokes


def test_glyph_stroke_count() -> None:
    glyph = glyph_for_digit(Scheme.S60, 12)
    strokes = glyph_strokes(glyph, 50)
    assert len(strokes) == 3  # base + two arms



def test_zero_digit_is_base_only() -> None:
    glyph = glyph_for_digit(Scheme.S64, 0)
    assert glyph.arms == frozenset()
    assert len(glyph_strokes(glyph, 20)) == 1
