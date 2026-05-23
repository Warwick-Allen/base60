"""Stroke curve definitions for glyph rendering."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.floating]


def stroke(style: int, x: FloatArray) -> tuple[FloatArray, FloatArray]:
    """Return upper and lower boundary curves for a stroke style.

    Parameters
    ----------
    style:
        Stroke identifier (supported: 60, 64).
    x:
        Sample positions along the stroke axis.

    Returns
    -------
    y1, y2:
        Boundary arrays with the same shape as ``x``.
    """
    x = np.asarray(x, dtype=float)
    match style:
        case 60:
            return _stroke_60(x)
        case 64:
            return _stroke_64(x)
        case _:
            raise ValueError(f"Unknown stroke style: {style}")


def _stroke_60(x: FloatArray) -> tuple[FloatArray, FloatArray]:
    y1 = (1 - (4 * x - 1) ** 2) / 4
    # log(2x) is undefined at x=0; limit of y2 is 0 there (y1=0, denom→∞)
    y2 = np.zeros_like(y1)
    positive = x > 0
    y2[positive] = y1[positive] / (1 - np.log(2 * x[positive]))
    return y1, y2


def _stroke_64(x: FloatArray) -> tuple[FloatArray, FloatArray]:
    y1 = (1 - np.abs(4 * x - 1) ** 0.5) / 2
    y2 = y1 * 4 / 5
    return y1, y2
