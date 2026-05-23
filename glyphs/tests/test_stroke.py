"""Tests for stroke curve computation."""

from __future__ import annotations

import numpy as np
import pytest

from glyphs.stroke import stroke


@pytest.mark.parametrize("style", [60, 64])
def test_stroke_returns_matching_shapes(style: int) -> None:
    x = np.linspace(0, 0.5, 50)
    y1, y2 = stroke(style, x)
    assert y1.shape == x.shape
    assert y2.shape == x.shape
    assert np.all(np.isfinite(y1))
    assert np.all(np.isfinite(y2))


def test_stroke_60_at_origin() -> None:
    x = np.array([0.0, 0.1, 0.5])
    y1, y2 = stroke(60, x)
    assert y1[0] == pytest.approx(0.0)
    assert y2[0] == pytest.approx(0.0)


def test_unknown_style_raises() -> None:
    with pytest.raises(ValueError, match="Unknown stroke style"):
        stroke(99, np.linspace(0, 0.5, 10))
