"""Line-of-sight checks for simple enemy shooting."""

from __future__ import annotations

from config.settings import TILE_SIZE
from game.entities.tank import Direction, Tank
from game.world.tiles import TileMap, blocks_bullets


def choose_enemy_shot_target(
    tile_map: TileMap,
    enemy: Tank,
    player: Tank,
    eagle_position: tuple[int, int],
) -> str | None:
    """Return the preferred line-of-sight target if one is visible."""
    if has_clear_tile_line(tile_map, tank_tile(enemy), eagle_position):
        return "eagle"
    if has_clear_tile_line(tile_map, tank_tile(enemy), tank_tile(player)):
        return "player"
    return None


def choose_enemy_shot_direction(
    tile_map: TileMap,
    enemy: Tank,
    player: Tank,
    eagle_position: tuple[int, int],
) -> Direction | None:
    """Return the direction the enemy should face before firing."""
    enemy_pos = tank_tile(enemy)
    if has_clear_tile_line(tile_map, enemy_pos, eagle_position):
        return direction_between(enemy_pos, eagle_position)
    player_pos = tank_tile(player)
    if has_clear_tile_line(tile_map, enemy_pos, player_pos):
        return direction_between(enemy_pos, player_pos)
    return None


def tank_tile(tank: Tank) -> tuple[int, int]:
    return (
        round((tank.x - TILE_SIZE / 2) / TILE_SIZE),
        round((tank.y - TILE_SIZE / 2) / TILE_SIZE),
    )


def direction_between(start: tuple[int, int], end: tuple[int, int]) -> Direction | None:
    """Return the cardinal direction from one tile to another on a shared lane."""
    start_x, start_y = start
    end_x, end_y = end
    if start_x == end_x:
        if end_y < start_y:
            return Direction.UP
        if end_y > start_y:
            return Direction.DOWN
        return None
    if start_y == end_y:
        if end_x < start_x:
            return Direction.LEFT
        if end_x > start_x:
            return Direction.RIGHT
        return None
    return None


def has_clear_tile_line(
    tile_map: TileMap,
    start: tuple[int, int],
    end: tuple[int, int],
) -> bool:
    """Return whether two tiles share a row or column with no blocking tiles between."""
    start_x, start_y = start
    end_x, end_y = end
    if start_x != end_x and start_y != end_y:
        return False

    if start_x == end_x:
        for tile_y in range(min(start_y, end_y) + 1, max(start_y, end_y)):
            if blocks_bullets(tile_map.tile_at(start_x, tile_y)):
                return False
        return True

    for tile_x in range(min(start_x, end_x) + 1, max(start_x, end_x)):
        if blocks_bullets(tile_map.tile_at(tile_x, start_y)):
            return False
    return True
