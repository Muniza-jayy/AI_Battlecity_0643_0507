"""Projectile stepping and hit resolution."""

from __future__ import annotations

from enum import StrEnum

from config.settings import TILE_SIZE
from game.entities.bullet import Bullet
from game.world.tiles import TileMap, TileType, blocks_bullets, is_destructible


class BulletHit(StrEnum):
    NONE = "none"
    BOUNDS = "bounds"
    BRICK = "brick"
    STEEL = "steel"
    EAGLE = "eagle"


def advance_bullet(bullet: Bullet, tile_map: TileMap) -> BulletHit:
    """Move a bullet forward and resolve the first tile it hits."""
    if not bullet.active:
        return BulletHit.NONE

    steps = max(1, int(bullet.speed))
    distance_per_step = bullet.speed / steps

    for _ in range(steps):
        bullet.x += bullet.dx * distance_per_step
        bullet.y += bullet.dy * distance_per_step

        if bullet_out_of_bounds(bullet, tile_map):
            bullet.active = False
            return BulletHit.BOUNDS

        tile_x = int(bullet.x // TILE_SIZE)
        tile_y = int(bullet.y // TILE_SIZE)
        tile_type = tile_map.tile_at(tile_x, tile_y)
        if not blocks_bullets(tile_type):
            continue

        bullet.active = False
        if is_destructible(tile_type):
            destroy_tile(tile_map, tile_x, tile_y)
            return BulletHit.BRICK
        if tile_type is TileType.STEEL:
            return BulletHit.STEEL
        if tile_type is TileType.EAGLE:
            return BulletHit.EAGLE
        return BulletHit.NONE

    return BulletHit.NONE


def bullet_out_of_bounds(bullet: Bullet, tile_map: TileMap) -> bool:
    return (
        bullet.x < 0
        or bullet.y < 0
        or bullet.x >= tile_map.width * TILE_SIZE
        or bullet.y >= tile_map.height * TILE_SIZE
    )


def destroy_tile(tile_map: TileMap, tile_x: int, tile_y: int) -> None:
    """Replace a destructible tile with empty space."""
    row = list(tile_map.tiles[tile_y])
    row[tile_x] = TileType.EMPTY
    mutable_rows = [list(existing_row) for existing_row in tile_map.tiles]
    mutable_rows[tile_y] = row
    tile_map.tiles = tuple(tuple(existing_row) for existing_row in mutable_rows)
