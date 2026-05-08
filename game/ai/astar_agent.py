"""A* pathing for Armor Tanks."""

from __future__ import annotations

from heapq import heappop, heappush

from game.ai.bfs_agent import eagle_adjacent_tiles, current_tile, manhattan_distance, neighbor_tiles, reconstruct_path
from game.entities.tank import Tank
from game.world.tiles import TileMap


def astar_path_to_eagle(
    tile_map: TileMap,
    enemy: Tank,
    eagle_position: tuple[int, int],
) -> list[tuple[int, int]]:
    """Return an A* path toward an eagle-adjacent goal."""
    start = current_tile(enemy)
    goals = eagle_adjacent_tiles(tile_map, eagle_position)
    return astar_path(tile_map, start, goals)


def astar_path(
    tile_map: TileMap,
    start: tuple[int, int],
    goals: set[tuple[int, int]],
) -> list[tuple[int, int]]:
    if not goals:
        return [start]
    if start in goals:
        return [start]

    frontier: list[tuple[int, int, tuple[int, int]]] = []
    parents: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    costs: dict[tuple[int, int], int] = {start: 0}
    heappush(frontier, (distance_to_goals(start, goals), 0, start))

    while frontier:
        _, cost_so_far, current = heappop(frontier)
        if current in goals:
            return reconstruct_path(parents, current)
        if cost_so_far > costs[current]:
            continue

        for neighbor in neighbor_tiles(tile_map, current):
            new_cost = cost_so_far + 1
            if new_cost >= costs.get(neighbor, new_cost + 1):
                continue
            parents[neighbor] = current
            costs[neighbor] = new_cost
            priority = new_cost + distance_to_goals(neighbor, goals)
            heappush(frontier, (priority, new_cost, neighbor))

    return [start]


def distance_to_goals(tile: tuple[int, int], goals: set[tuple[int, int]]) -> int:
    return min(manhattan_distance(tile, goal) for goal in goals)
