"""BFS pathing for the first Basic Tank enemy."""

from __future__ import annotations

from collections import deque

from game.entities.tank import Direction, Tank
from game.world.tiles import TileMap, is_passable_for_tanks
from config.settings import TILE_SIZE


def choose_basic_direction(
    tile_map: TileMap,
    enemy: Tank,
    eagle_position: tuple[int, int],
) -> Direction | None:
    """Return the first BFS step toward a reachable tile adjacent to the eagle."""
    path = basic_path_to_eagle(tile_map, enemy, eagle_position)
    if len(path) < 2:
        return None

    next_tile = path[1]
    dx = next_tile[0] - current_tile(enemy)[0]
    dy = next_tile[1] - current_tile(enemy)[1]
    if dx > 0:
        return Direction.RIGHT
    if dx < 0:
        return Direction.LEFT
    if dy > 0:
        return Direction.DOWN
    if dy < 0:
        return Direction.UP
    return None


def basic_path_to_eagle(
    tile_map: TileMap,
    enemy: Tank,
    eagle_position: tuple[int, int],
) -> list[tuple[int, int]]:
    """Return the BFS tile path for a basic tank toward the eagle approach lane."""
    start = current_tile(enemy)
    goal_tiles = eagle_adjacent_tiles(tile_map, eagle_position)
    return bfs_path(tile_map, start, goal_tiles)


def current_tile(tank: Tank) -> tuple[int, int]:
    return (
        round((tank.x - TILE_SIZE / 2) / TILE_SIZE),
        round((tank.y - TILE_SIZE / 2) / TILE_SIZE),
    )


def eagle_adjacent_tiles(tile_map: TileMap, eagle_position: tuple[int, int]) -> set[tuple[int, int]]:
    """Return the reachable tiles from which an enemy can attack the eagle."""
    ex, ey = eagle_position
    candidates = {(ex - 1, ey), (ex + 1, ey), (ex, ey - 1), (ex, ey + 1)}
    goals: set[tuple[int, int]] = set()
    for tx, ty in candidates:
        if tx < 0 or ty < 0 or tx >= tile_map.width or ty >= tile_map.height:
            continue
        if is_passable_for_tanks(tile_map.tile_at(tx, ty)):
            goals.add((tx, ty))
    return goals


def neighbor_tiles(
    tile_map: TileMap,
    tile: tuple[int, int],
) -> list[tuple[int, int]]:
    """Return passable neighbor tiles in movement order."""
    x, y = tile
    neighbors: list[tuple[int, int]] = []
    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
        if nx < 0 or ny < 0 or nx >= tile_map.width or ny >= tile_map.height:
            continue
        if not is_passable_for_tanks(tile_map.tile_at(nx, ny)):
            continue
        neighbors.append((nx, ny))
    return neighbors


def manhattan_distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def bfs_path(
    tile_map: TileMap,
    start: tuple[int, int],
    goals: set[tuple[int, int]],
) -> list[tuple[int, int]]:
    """Return a BFS path from start to the closest goal tile."""
    if start in goals:
        return [start]

    queue = deque([start])
    parents: dict[tuple[int, int], tuple[int, int] | None] = {start: None}

    while queue:
        x, y = queue.popleft()
        for neighbor in neighbor_tiles(tile_map, (x, y)):
            if neighbor in parents:
                continue
            parents[neighbor] = (x, y)
            if neighbor in goals:
                return reconstruct_path(parents, neighbor)
            queue.append(neighbor)

    return [start]


def reconstruct_path(
    parents: dict[tuple[int, int], tuple[int, int] | None],
    end: tuple[int, int],
) -> list[tuple[int, int]]:
    path = [end]
    cursor = parents[end]
    while cursor is not None:
        path.append(cursor)
        cursor = parents[cursor]
    path.reverse()
    return path
