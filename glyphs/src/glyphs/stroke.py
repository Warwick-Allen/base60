"""Stroke curve definitions for glyph rendering."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.floating]


def stroke(
    style: str,
    n: int,
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Sample a stroke style over ``[x_min, x_max]``.

    Parameters
    ----------
    style:
        Stroke identifier (supported: ``'base'``, ``'60'``, ``'64'``).
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
    match style:
        case "base":
            x, y1, y2 = _stroke_base(int(n/4))
        case "60":
            x, y1, y2 = _stroke_60(n)
        case "64":
            x, y1, y2 = _stroke_64(n)
        case _:
            raise ValueError(f"Unknown stroke style: {style}")
    return x, y1, y2


def _stroke_base(n: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    x_min = -1/16
    x_max =  1/16
    x = np.linspace(x_min, x_max, n, dtype=float)
    i = abs(x) <= 1 / 16
    y1 = np.zeros_like(x)
    y1[i] = (1 + np.cos(16 * np.pi * x[i])) / 4 - 1 / 2
    y2 = np.zeros_like(x) - 1 / 2
    return x, y1, y2


def _stroke_60(n: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    x_min = 0
    x_max = 1/2
    x = np.linspace(x_min, x_max, n, dtype=float)
    i = x > 0
    y1 = np.zeros_like(x)
    y1[i] = (1 - (4 * x[i] - 1) ** 2) / 4
    y2 = np.zeros_like(x)
    y2[i] = y1[i] / (1 - np.log(2 * x[i]))
    return x, y1, y2


def _stroke_64(n: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    x_min = 0
    x_max = 1/2
    x = np.linspace(x_min, x_max, n, dtype=float)
    i = x > 0
    y1 = np.zeros_like(x)
    y1[i] = (1 - np.abs(4 * x[i] - 1) ** 0.5) / 2
    y2 = 4 * y1 / 5
    return x, y1, y2
