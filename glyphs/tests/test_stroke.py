"""Tests for stroke curve computation."""

from __future__ import annotations

import numpy as np
import pytest

from glyphs.encoding import glyph_for_digit
from glyphs.placement import Placement
from glyphs.scheme import Scheme
from glyphs.stroke import glyph_strokes, sample_arm, sample_stem


def test_sample_stem_shapes() -> None:
    for scheme in Scheme:
        geom = sample_stem(scheme, 40)
        assert geom.x_upper.shape == geom.y1.shape == geom.y2.shape
        assert np.all(np.isfinite(geom.y1))


@pytest.mark.parametrize("placement", list(Placement))
def test_sample_arm_finite(placement: Placement) -> None:
    for scheme in (Scheme.S60, Scheme.S64):
        geom = sample_arm(scheme, placement, 50)
        assert np.all(np.isfinite(geom.y1))
        assert np.all(np.isfinite(geom.y2))


def test_stroke_60_arm_at_origin() -> None:
    geom = sample_arm(Scheme.S60, Placement.BIT_4, 3)
    assert geom.y1[0] == pytest.approx(0.0)
    assert geom.y2[0] == pytest.approx(0.0)


def test_n_too_small_raises() -> None:
    with pytest.raises(ValueError, match="n must be at least 2"):
        sample_arm(Scheme.S64, Placement.BIT_0, 1)


def test_glyph_strokes_from_digit() -> None:
    glyph = glyph_for_digit(Scheme.S60, 5)  # bits 0 and 2
    strokes = glyph_strokes(glyph, 30)
    assert len(strokes) == 1 + 2
