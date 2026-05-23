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
        Stroke identifier (supported: ``'60base'``, ``'64base'``, ``'60'``, ``'64'``).
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
        case "60base":
            x, y1, y2 = _stroke_60base(int(n/4))
        case "64base":
            x, y1, y2 = _stroke_64base(int(n/4))
        case "60":
            x, y1, y2 = _stroke_60(n)
        case "64":
            x, y1, y2 = _stroke_64(n)
        case _:
            raise ValueError(f"Unknown stroke style: {style}")
    return x, y1, y2


def _stroke_60base(n: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    width = 1/32
    x_min = -width
    x_max =  width
    x = np.linspace(x_min, x_max, n, dtype=float)
    y1 = np.zeros_like(x)
    y1 = (1 + np.cos(np.pi * x / width)) / 4 - 1 / 2
    y2 = np.zeros_like(x) - 1 / 2
    return x, y1, y2


def _stroke_64base(n: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    width = 1/64
    x_min = -width
    x_max =  width
    x = np.linspace(x_min, x_max, n, dtype=float)
    y1 = np.zeros_like(x)
    y1 = (1 + np.cos(np.pi * x / width)) / 4 - 1 / 2
    y1 = ((2*y1 + 1)**(1/16) - 1)/2
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
