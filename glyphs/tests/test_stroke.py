"""Tests for stroke curve computation."""

from __future__ import annotations

import numpy as np
import pytest

from glyphs.stroke import stroke


@pytest.mark.parametrize("style", ["60", "64"])
def test_stroke_returns_matching_shapes(style: str) -> None:
    x, y1, y2 = stroke(style, 0.0, 0.5, 50)
    assert x.shape == (50,)
    assert y1.shape == x.shape
    assert y2.shape == x.shape
    assert np.all(np.isfinite(y1))
    assert np.all(np.isfinite(y2))
    assert x[0] == pytest.approx(0.0)
    assert x[-1] == pytest.approx(0.5)


def test_stroke_60_at_origin() -> None:
    x, y1, y2 = stroke("60", 0.0, 0.5, 3)
    assert x[0] == pytest.approx(0.0)
    assert y1[0] == pytest.approx(0.0)
    assert y2[0] == pytest.approx(0.0)


def test_stroke_accepts_float_n() -> None:
    x, y1, y2 = stroke("64", 0.0, 0.5, 50.0)
    assert len(x) == 50


def test_n_too_small_raises() -> None:
    with pytest.raises(ValueError, match="n must be at least 2"):
        stroke("64", 0.0, 0.5, 1)


def test_unknown_style_raises() -> None:
    with pytest.raises(ValueError, match="Unknown stroke style"):
        stroke("99", 0.0, 0.5, 10)
