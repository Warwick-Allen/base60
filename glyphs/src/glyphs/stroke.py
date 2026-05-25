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


def sample_stem(scheme: Scheme, n: int) -> StrokeGeometry:
    """Sample the stem stroke for a scheme."""
    n = int(n)
    base_n = max(2, int(n / _BASE_N_RATIO))
    match scheme:
        case Scheme.S60:
            return _as_geometry(*_sample_60stem(base_n))
        case Scheme.S64:
            return _as_geometry(*_sample_64stem(base_n))


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
    """Sample stem plus all arm strokes for a glyph."""
    n = int(n)
    strokes = [sample_stem(glyph.scheme, n)]
    for placement in sorted(glyph.arms, key=lambda p: p.bit_index):
        strokes.append(sample_arm(glyph.scheme, placement, n))
    return strokes


def _sample_stem_common(n: int, thinness: int, coeffs: tuple[float, float, float, float]) -> tuple[FloatArray, FloatArray, FloatArray]:
    width = 1/(2*thinness)
    x = np.linspace(-width, width, n, dtype=float)
    y1 = np.zeros_like(x)/2
    i = x > 0
    xi = thinness * x[i]
    y1[x > 0] = (coeffs[0]*xi**3 + coeffs[1]*xi**2 + coeffs[2]*xi + coeffs[3])/2
    y1[x < 0] = y1[x > 0][::-1]
    y1 /= 2
    y2 = np.full_like(x, -1/4)
    return x, y1, y2


def _sample_60stem(n: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    return _sample_stem_common(n, 16, (16, -12, 0, 0))


def _sample_64stem(n: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    return _sample_stem_common(n, 32, (25/2, -41/4, 0, 0))


def _sample_arm_common(
    n: int,
    sign: int,
    coeffs1: tuple[float, float, float, float],
    coeffs2: tuple[float, float, float, float],
    *,
    split: float = 1/8,
    mirror_at: float | None = None,
) -> tuple[FloatArray, FloatArray, FloatArray]:
    x = np.linspace(0, 0.5, n, dtype=float)

    def eval_piecewise(values: FloatArray) -> FloatArray:
        y = np.zeros_like(values)
        i1 = values < split
        i2 = ~i1
        if np.any(i1):
            y[i1] = (
                  coeffs1[0]*values[i1]**3
                + coeffs1[1]*values[i1]**2
                + coeffs1[2]*values[i1]
                + coeffs1[3]
            )
        if np.any(i2):
            y[i2] = (
                  coeffs2[0]*values[i2]**3
                + coeffs2[1]*values[i2]**2
                + coeffs2[2]*values[i2]
                + coeffs2[3]
            )
        return y

    y1 = np.zeros_like(x)
    if mirror_at is None:
        y1 = eval_piecewise(x)
    else:
        left  = x <  mirror_at
        right = x >= mirror_at
        if np.any(left):
            y1[left] = eval_piecewise(x[left])
        if np.any(right):
            y1[right] = eval_piecewise(0.5 - x[right])
    y1 *= sign
    y2 = 3/4*y1
    return x, y1, y2


def _sample_60_arm(n: int, sign: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    return _sample_arm_common(
        n,
        sign,
        (     -8,    3,   3/8, 0     ),
        (-184/27, 23/9, 31/72, -1/432)
    )


def _sample_64_arm(n: int, sign: int) -> tuple[FloatArray, FloatArray, FloatArray]:
    return _sample_arm_common(
        n,
        sign,
        (24,  -9, 11/8,  0   ),
        (72, -27, 29/8, -3/32),
        split = 1/8,
        mirror_at = 1/4,
    )


def stroke(
    style: str,
    n: int,
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Deprecated: sample a single stroke by legacy style name."""
    warnings.warn(
        "stroke() is deprecated; use sample_stem, sample_arm, or glyph_strokes",
        DeprecationWarning,
        stacklevel=2,
    )
    n = int(n)
    if n < 2:
        raise ValueError(f"n must be at least 2, got {n}")
    match style:
        case "60stem":
            geom = sample_stem(Scheme.S60, n)
        case "64stem":
            geom = sample_stem(Scheme.S64, n)
        case "60":
            geom = sample_arm(Scheme.S60, Placement.BIT_2, n)
        case "64":
            geom = sample_arm(Scheme.S64, Placement.BIT_4, n)
        case _:
            raise ValueError(f"Unknown stroke style: {style}")
    return geom.x_upper, geom.y1, geom.y2
