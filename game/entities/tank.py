"""Shared tank data structures."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Direction(StrEnum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


@dataclass
class Tank:
    """Minimal continuous-position tank state."""

    x: float
    y: float
    size: int
    speed: float
    facing: Direction


def direction_vector(direction: Direction) -> tuple[int, int]:
    vectors = {
        Direction.UP: (0, -1),
        Direction.DOWN: (0, 1),
        Direction.LEFT: (-1, 0),
        Direction.RIGHT: (1, 0),
    }
    return vectors[direction]
