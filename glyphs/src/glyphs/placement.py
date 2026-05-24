"""Arm placement slots (six-bit bitmap indices)."""

from __future__ import annotations

from enum import IntEnum

import numpy as np

ROTATION_BY_BIT: tuple[float, ...] = (
    np.pi,
    np.pi,
    np.pi/2,
    np.pi/2,
    0.0,
    0.0,
)

# CLI token for each bit index
_TOKEN_BY_BIT: tuple[str, ...] = ("180+", "180-", "90+", "90-", "0+", "0-")
_BIT_BY_TOKEN: dict[str, int] = {token: i for i, token in enumerate(_TOKEN_BY_BIT)}


class Placement(IntEnum):
    """Arm slot keyed by bitmap bit index (0 = LSB)."""

    BIT_0 = 0
    BIT_1 = 1
    BIT_2 = 2
    BIT_3 = 3
    BIT_4 = 4
    BIT_5 = 5

    @property
    def bit_index(self) -> int:
        return int(self.value)

    def rotation_angle(self) -> float:
        return ROTATION_BY_BIT[self.bit_index]

    def sign(self) -> int:
        return 1 if self.bit_index % 2 == 0 else -1

    @classmethod
    def from_bit(cls, bit: int) -> Placement:
        if not 0 <= bit < 6:
            raise ValueError(f"bit index must be 0..5, got {bit}")
        return cls(bit)

    @classmethod
    def parse(cls, token: str) -> Placement:
        key = token.strip().replace(" ", "")
        if key not in _BIT_BY_TOKEN:
            raise ValueError(
                f"Unknown placement {token!r}; expected one of {list(_TOKEN_BY_BIT)}"
            )
        return cls.from_bit(_BIT_BY_TOKEN[key])

    def format_token(self) -> str:
        return _TOKEN_BY_BIT[self.bit_index]
