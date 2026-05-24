"""Glyphs — glyph plotting and visualisation."""

from glyphs.encoding import digit_from_glyph, glyph_for_digit, placements_from_digit
from glyphs.glyph import Glyph
from glyphs.placement import Placement
from glyphs.plot import plot_glyph
from glyphs.scheme import Scheme
from glyphs.stroke import StrokeGeometry, glyph_strokes, sample_arm, sample_base

__all__ = [
    "Glyph",
    "Placement",
    "Scheme",
    "StrokeGeometry",
    "digit_from_glyph",
    "glyph_for_digit",
    "glyph_strokes",
    "placements_from_digit",
    "plot_glyph",
    "sample_arm",
    "sample_base",
    "__version__",
]
__version__ = "0.1.0"
