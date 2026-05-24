"""Stroke curve sampling for glyph rendering."""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from glyphs.glyph import Glyph
from glyphs.placement import Placement
from glyphs.scheme import Scheme

FloatArray = NDArray[np.floating]

_BASE_N_RATIO = 4


@dataclass(frozen=True)
class StrokeGeometry:
    """Filled stroke boundary (upper and lower edges may use different x)."""

    x_upper: FloatArray
    y1: FloatArray
    x_lower: FloatArray
    y2: FloatArray


def _as_geometry(
    x: FloatArray, y1: FloatArray, y2: FloatArray
) -> StrokeGeometry:
    return StrokeGeometry(x, y1, x, y2)


def _rotate_stroke(
    x: FloatArray, y1: FloatArray, y2: FloatArray, theta: float
) -> StrokeGeometry:
    c, s = np.cos(theta), np.sin(theta)
    return StrokeGeometry(
        x * c - y1 * s,
        x * s + y1 * c,
        x * c - y2 * s,
        x * s + y2 * c,
    )


def sample_base(scheme: Scheme, n: int) -> StrokeGeometry:
    """Sample the base stroke for a scheme."""
    n = int(n)
    base_n = max(2, int(n / _BASE_N_RATIO))
    match scheme:
        case Scheme.S60:
            return _as_geometry(*_sample_60base(base_n))
        case Scheme.S64:
            return _as_geometry(*_sample_64base(base_n))


def sample_arm(scheme: Scheme, placement: Placement, n: int) -> StrokeGeometry:
    """Sample one arm stroke at the given placement."""
    n = int(n)
    if n < 2:
        raise ValueError(f"n must be at least 2, got {n}")
    sign = placement.sign()
    theta = placement.rotation_angle()
    match scheme:
        case Scheme.S60:
            x, y1, y2 = _sample_60_arm(n, sign)
        case Scheme.S64:
            x, y1, y2 = _sample_64_arm(n, sign)
    return _rotate_stroke(x, y1, y2, theta)


def glyph_strokes(glyph: Glyph, n: int) -> list[StrokeGeometry]:
    """Sample base plus all arm strokes for a glyph."""
    n = int(n)
    strokes = [sample_base(glyph.scheme, n)]
    for placement in sorted(glyph.arms, key=lambda p: p.bit_index):
        strokes.append(sample_arm(glyph.scheme, placement, n))
    return strokes


def _sample_60base(n: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    width = 1 / 32
    x = np.linspace(-width, width, n, dtype=float)
    y1 = (1 + np.cos(np.pi * x / width)) / 4 - 1 / 2
    y2 = np.full_like(x, -1 / 2)
    return x, y1, y2


def _sample_64base(n: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    width = 1 / 96
    x = np.linspace(-width, width, n, dtype=float)
    y1 = (1 - (x / width) ** 4) ** 0.5 / 2 - 1 / 2
    y2 = np.full_like(x, -1 / 2)
    return x, y1, y2


def _sample_60_arm(n: int, sign: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    x = np.linspace(0, 0.5, n, dtype=float)
    y1 = np.zeros_like(x)
    y2 = np.zeros_like(x)
    positive = x > 0
    y1[positive] = sign * (1 - (4 * x[positive] - 1) ** 2) / 4 / (1 - np.log(2 * x[positive]))
    y2[positive] = 3 * y1[positive] / 4
    return x, y1, y2


def _sample_64_arm(n: int, sign: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    x = np.linspace(0, 0.5, n, dtype=float)
    y1 = np.zeros_like(x)
    y2 = np.zeros_like(x)
    positive = x > 0
    y1[positive] = sign * (1 - np.abs(4 * x[positive] - 1) ** 0.5) / 4
    y2[positive] = 4 * y1[positive] / 5
    return x, y1, y2


def stroke(
    style: str,
    n: int,
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Deprecated: sample a single stroke by legacy style name."""
    warnings.warn(
        "stroke() is deprecated; use sample_base, sample_arm, or glyph_strokes",
        DeprecationWarning,
        stacklevel=2,
    )
    n = int(n)
    if n < 2:
        raise ValueError(f"n must be at least 2, got {n}")
    match style:
        case "60base":
            geom = sample_base(Scheme.S60, n)
        case "64base":
            geom = sample_base(Scheme.S64, n)
        case "60":
            geom = sample_arm(Scheme.S60, Placement.BIT_2, n)
        case "64":
            geom = sample_arm(Scheme.S64, Placement.BIT_4, n)
        case _:
            raise ValueError(f"Unknown stroke style: {style}")
    return geom.x_upper, geom.y1, geom.y2
