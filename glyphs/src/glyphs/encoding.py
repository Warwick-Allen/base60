"""Bitmap digit encoding for glyph arms."""

from __future__ import annotations

from glyphs.glyph import Glyph
from glyphs.placement import Placement
from glyphs.scheme import Scheme


def placements_from_digit(digit: int) -> frozenset[Placement]:
    """Return arm placements for a 6-bit digit value."""
    return frozenset(Placement.from_bit(i) for i in range(6) if digit & (1 << i))


def glyph_for_digit(scheme: Scheme, digit: int) -> Glyph:
    """Build a glyph from a scheme digit (0..59 or 0..63)."""
    max_digit = scheme.max_digit()
    if not 0 <= digit <= max_digit:
        raise ValueError(
            f"digit {digit} out of range for scheme {scheme.value} (0..{max_digit})"
        )
    return Glyph(scheme, placements_from_digit(digit))


def digit_from_glyph(glyph: Glyph) -> int:
    """Encode arm placements as a 6-bit integer."""
    return sum(1 << p.bit_index for p in glyph.arms)
