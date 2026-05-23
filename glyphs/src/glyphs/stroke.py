"""Stroke curve definitions for glyph rendering."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.floating]


def stroke(
    style: str,
    x_min: float,
    x_max: float,
    n: int,
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Sample a stroke style over ``[x_min, x_max]``.

    Parameters
    ----------
    style:
        Stroke identifier (supported: ``'base'``, ``'60'``, ``'64'``).
    x_min, x_max:
        Endpoints of the sample range (inclusive).
    n:
        Number of sample points.

    Returns
    -------
    x, y1, y2:
        Sample positions and boundary arrays, each of length ``n``.
    """
    n = int(n)
    if n < 2:
        raise ValueError(f"n must be at least 2, got {n}")
    x = np.linspace(x_min, x_max, n, dtype=float)
    match style:
        case "base":
            y1, y2 = _stroke_base(x)
        case "60":
            y1, y2 = _stroke_60(x)
        case "64":
            y1, y2 = _stroke_64(x)
        case _:
            raise ValueError(f"Unknown stroke style: {style}")
    return x, y1, y2


def _stroke_base(x: FloatArray) -> tuple[FloatArray, FloatArray]:
    i = abs(x) <= 1 / 16
    y1 = np.zeros_like(x)
    y1[i] = (1 + np.cos(16 * np.pi * x[i])) / 4 - 1 / 2
    y2 = np.zeros_like(x) - 1 / 2
    return y1, y2


def _stroke_60(x: FloatArray) -> tuple[FloatArray, FloatArray]:
    i = x > 0
    y1 = np.zeros_like(x)
    y1[i] = (1 - (4 * x[i] - 1) ** 2) / 4
    y2 = np.zeros_like(x)
    y2[i] = y1[i] / (1 - np.log(2 * x[i]))
    return y1, y2


def _stroke_64(x: FloatArray) -> tuple[FloatArray, FloatArray]:
    i = x > 0
    y1 = np.zeros_like(x)
    y1[i] = (1 - np.abs(4 * x[i] - 1) ** 0.5) / 2
    y2 = 4 * y1 / 5
    return y1, y2
