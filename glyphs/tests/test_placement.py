"""Tests for placement slots."""

from __future__ import annotations

import numpy as np
import pytest

from glyphs.placement import ROTATION_BY_BIT, Placement


@pytest.mark.parametrize(
    ("bit", "angle", "sign"),
    [
        (0, 0.0,      -1),
        (1, 0.0,       1),
        (2, np.pi/2,  -1),
        (3, np.pi/2,   1),
        (4, np.pi,    -1),
        (5, np.pi,     1),
    ],
)
def test_placement_from_bit(bit: int, angle: float, sign: int) -> None:
    p = Placement.from_bit(bit)
    assert p.bit_index == bit
    assert p.rotation_angle() == pytest.approx(angle)
    assert p.sign() == sign


@pytest.mark.parametrize("placement", list(Placement))
def test_parse_format_round_trip(placement: Placement) -> None:
    token = placement.format_token()
    assert Placement.parse(token) is placement


def test_invalid_bit_raises() -> None:
    with pytest.raises(ValueError, match="bit index"):
        Placement.from_bit(6)


def test_rotation_by_bit_length() -> None:
    assert len(ROTATION_BY_BIT) == 6
