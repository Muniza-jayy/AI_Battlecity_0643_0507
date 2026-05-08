"""Projectile state and spawning helpers."""

from __future__ import annotations

from dataclasses import dataclass

from config.balance import PLAYER_BULLET_RADIUS, PLAYER_BULLET_SPEED
from game.entities.tank import Direction, Tank, direction_vector


@dataclass
class Bullet:
    """A simple straight-moving projectile."""

    x: float
    y: float
    dx: float
    dy: float
    speed: float
    radius: int
    active: bool = True


def spawn_bullet_from_tank(tank: Tank) -> Bullet:
    """Spawn a bullet slightly in front of the firing tank."""
    vx, vy = direction_vector(tank.facing)
    muzzle_offset = tank.size / 2 + PLAYER_BULLET_RADIUS + 2
    return Bullet(
        x=tank.x + vx * muzzle_offset,
        y=tank.y + vy * muzzle_offset,
        dx=float(vx),
        dy=float(vy),
        speed=PLAYER_BULLET_SPEED,
        radius=PLAYER_BULLET_RADIUS,
    )
