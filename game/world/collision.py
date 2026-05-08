"""Collision helpers for tanks against blocking tiles."""

from __future__ import annotations

from config.settings import TILE_SIZE
from game.world.tiles import TileMap, blocks_tanks


def tank_can_occupy(center_x: float, center_y: float, size: int, tile_map: TileMap) -> bool:
    """Return whether a tank body can occupy the given center position."""
    half_size = size / 2
    left = center_x - half_size
    top = center_y - half_size
    right = center_x + half_size - 1
    bottom = center_y + half_size - 1

    if left < 0 or top < 0:
        return False

    map_width_px = tile_map.width * TILE_SIZE
    map_height_px = tile_map.height * TILE_SIZE
    if right >= map_width_px or bottom >= map_height_px:
        return False

    min_tile_x = int(left // TILE_SIZE)
    max_tile_x = int(right // TILE_SIZE)
    min_tile_y = int(top // TILE_SIZE)
    max_tile_y = int(bottom // TILE_SIZE)

    for tile_y in range(min_tile_y, max_tile_y + 1):
        for tile_x in range(min_tile_x, max_tile_x + 1):
            if blocks_tanks(tile_map.tile_at(tile_x, tile_y)):
                return False

    return True
