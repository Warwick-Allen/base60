"""Stroke curve definitions for glyph rendering."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.floating]


def stroke(style: str, x: FloatArray) -> tuple[FloatArray, FloatArray]:
    """Return upper and lower boundary curves for a stroke style.

    Parameters
    ----------
    style:
        Stroke identifier (supported: '60', '64').
    x:
        Sample positions along the stroke axis.

    Returns
    -------
    y1, y2:
        Boundary arrays with the same shape as ``x``.
    """
    x = np.asarray(x, dtype=float)
    match style:
        case 'base':
            return _stroke_base(x)
        case '60':
            return _stroke_60(x)
        case '64':
            return _stroke_64(x)
        case _:
            raise ValueError(f"Unknown stroke style: {style}")


def _stroke_base(x: FloatArray) -> tuple[FloatArray, FloatArray]:
    i = abs(x) <= 1/16
    y1 = np.zeros_like(x)
    y1[i] = (1 + np.cos(16*np.pi*x[i]))/4 - 1/2
    y2 = np.zeros_like(x) - 1/2
    return y1, y2


def _stroke_60(x: FloatArray) -> tuple[FloatArray, FloatArray]:
    i = x > 0
    y1 = np.zeros_like(x)
    y1[i] = (1 - (4*x[i] - 1)**2)/4
    y2 = np.zeros_like(x)
    y2[i] = y1[i]/(1 - np.log(2*x[i]))
    return y1, y2


def _stroke_64(x: FloatArray) -> tuple[FloatArray, FloatArray]:
    i = x > 0
    y1 = np.zeros_like(x)
    y1[i] = (1 - np.abs(4*x[i] - 1)**(1/2))/2
    y2 = 4*y1/5
    return y1, y2

