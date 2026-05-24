"""Tests for glyph plotting."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from glyphs.encoding import glyph_for_digit
from glyphs.plot import plot_glyph
from glyphs.scheme import Scheme


def test_plot_glyph_returns_axes() -> None:
    glyph = glyph_for_digit(Scheme.S60, 12)
    ax = plot_glyph(glyph, n=30)
    assert ax is plt.gca()
    plt.close()
