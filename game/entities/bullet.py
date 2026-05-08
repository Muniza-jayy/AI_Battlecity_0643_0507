"""Projectile state and spawning helpers."""

from __future__ import annotations

from dataclasses import dataclass

from config.balance import (
    ENEMY_BULLET_RADIUS,
    ENEMY_BULLET_SPEED,
    PLAYER_BULLET_RADIUS,
    PLAYER_BULLET_SPEED,
)
from game.entities.tank import Tank, direction_vector


@dataclass
class Bullet:
    """A simple straight-moving projectile."""

    x: float
    y: float
    dx: float
    dy: float
    speed: float
    radius: int
    owner: str
    owner_id: int | None = None
    active: bool = True


def spawn_bullet_from_tank(tank: Tank, owner: str, owner_id: int | None = None) -> Bullet:
    """Spawn a bullet slightly in front of the firing tank."""
    vx, vy = direction_vector(tank.facing)
    muzzle_offset = tank.size / 2 + PLAYER_BULLET_RADIUS + 2
    speed = PLAYER_BULLET_SPEED if owner == "player" else ENEMY_BULLET_SPEED
    radius = PLAYER_BULLET_RADIUS if owner == "player" else ENEMY_BULLET_RADIUS
    return Bullet(
        x=tank.x + vx * muzzle_offset,
        y=tank.y + vy * muzzle_offset,
        dx=float(vx),
        dy=float(vy),
        speed=speed,
        radius=radius,
        owner=owner,
        owner_id=owner_id,
    )
