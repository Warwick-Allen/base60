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


def _sample_base_common(n: int, thinness: int, coeffs: tuple[float, float, float, float]) -> tuple[FloatArray, FloatArray, FloatArray]:
    width = 1/(2*thinness)
    x = np.linspace(-width, width, n, dtype=float)
    y1 = np.zeros_like(x)/2
    i = x > 0
    xi = thinness * x[i]
    y1[x > 0] = (coeffs[0]*xi**3 + coeffs[1]*xi**2 + coeffs[2]*xi + coeffs[3])/2
    y1[x < 0] = y1[x > 0][::-1]
    y2 = np.full_like(x, -1/2)
    return x, y1, y2


def _sample_60base(n: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    return _sample_base_common(n, 16, (16, -12, 0, 0))


def _sample_64base(n: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    return _sample_base_common(n, 32, (25/2, -41/4, 0, 0))


def _sample_60_arm(n: int, sign: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    x = np.linspace(0, 0.5, n, dtype=float)
    y1 = np.zeros_like(x)
    i1 = x <  1/8
    i2 = x >= 1/8
    y1[i1] = sign*(   -8   *x[i1]**3 +  3  *x[i1]**2 +  3/ 8*x[i1]         )
    y1[i2] = sign*( -184/27*x[i2]**3 + 23/9*x[i2]**2 + 31/72*x[i2] - 1/432 )
    y2 = 3/4*y1
    return x, y1, y2


def _sample_64_arm(n: int, sign: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    x = np.linspace(0, 0.5, n, dtype=float)
    y1 = np.zeros_like(x)
    i1 = (x <  1/8) & (x < 1/4)
    i2 = (x >= 1/8) & (x < 1/4)
    y1[i1] = sign*(   24   *x[i1]**3 -  9  *x[i1]**2 + 11/ 8*x[i1]         )
    y1[i2] = sign*(   72   *x[i2]**3 - 27  *x[i2]**2 + 29/ 8*x[i2] - 3/ 32 )
    y1[x >= 1/4] = y1[x < 1/4][::-1]
    y2 = 3/4*y1
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
