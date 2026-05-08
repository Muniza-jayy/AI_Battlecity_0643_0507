"""Greedy Best-First Search pathing for Fast Tanks."""

from __future__ import annotations

from heapq import heappop, heappush

from game.ai.bfs_agent import eagle_adjacent_tiles, current_tile, manhattan_distance, neighbor_tiles, reconstruct_path
from game.entities.tank import Tank
from game.world.tiles import TileMap


def greedy_path_to_eagle(
    tile_map: TileMap,
    enemy: Tank,
    eagle_position: tuple[int, int],
) -> list[tuple[int, int]]:
    """Return a Greedy Best-First path toward an eagle-adjacent goal."""
    start = current_tile(enemy)
    goals = eagle_adjacent_tiles(tile_map, eagle_position)
    return greedy_path(tile_map, start, goals)


def greedy_path(
    tile_map: TileMap,
    start: tuple[int, int],
    goals: set[tuple[int, int]],
) -> list[tuple[int, int]]:
    if not goals:
        return [start]
    if start in goals:
        return [start]

    frontier: list[tuple[int, tuple[int, int]]] = []
    parents: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    heappush(frontier, (distance_to_goals(start, goals), start))

    while frontier:
        _, current = heappop(frontier)
        if current in goals:
            return reconstruct_path(parents, current)

        for neighbor in neighbor_tiles(tile_map, current):
            if neighbor in parents:
                continue
            parents[neighbor] = current
            heappush(frontier, (distance_to_goals(neighbor, goals), neighbor))

    return [start]


def distance_to_goals(tile: tuple[int, int], goals: set[tuple[int, int]]) -> int:
    return min(manhattan_distance(tile, goal) for goal in goals)
