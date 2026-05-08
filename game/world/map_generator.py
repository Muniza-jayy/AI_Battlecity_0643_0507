"""CSP-style random map generation with reachability validation."""

from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass

from config.levels import EAGLE_POSITION, ENEMY_SPAWNS, PLAYER_SPAWN
from config.settings import GRID_HEIGHT, GRID_WIDTH
from game.world.map_loader import build_tile_map
from game.world.tiles import TileMap, TileType, is_passable_for_tanks


TILE_SYMBOL_BY_TYPE: dict[TileType, str] = {
    TileType.EMPTY: ".",
    TileType.BRICK: "B",
    TileType.STEEL: "S",
    TileType.WATER: "W",
    TileType.FOREST: "F",
    TileType.EAGLE: "E",
}


@dataclass(frozen=True)
class GeneratorSpec:
    width: int = GRID_WIDTH
    height: int = GRID_HEIGHT
    player_spawn: tuple[int, int] = PLAYER_SPAWN
    enemy_spawns: tuple[tuple[int, int], ...] = ENEMY_SPAWNS
    eagle_position: tuple[int, int] = EAGLE_POSITION
    brick_count: int = 56
    steel_count: int = 26
    water_count: int = 22
    forest_count: int = 18


def generate_csp_map(seed: int | None = None, spec: GeneratorSpec = GeneratorSpec()) -> TileMap:
    """Generate a playable standard arena using constrained randomized placement."""
    rng = random.Random(seed)
    attempts = 0
    while attempts < 80:
        attempts += 1
        grid = [[TileType.EMPTY for _ in range(spec.width)] for _ in range(spec.height)]
        ex, ey = spec.eagle_position
        grid[ey][ex] = TileType.EAGLE
        fortified_counts = _protect_eagle(grid, spec, rng)

        reserved = reserved_tiles(spec)
        corridor = protected_corridor_tiles(spec)
        blocked_for_random = reserved | corridor
        cell_order = shuffled_candidate_cells(spec, rng, blocked_for_random)

        quotas = [
            (TileType.BRICK, max(0, spec.brick_count - fortified_counts[TileType.BRICK])),
            (TileType.STEEL, max(0, spec.steel_count - fortified_counts[TileType.STEEL])),
            (TileType.WATER, spec.water_count),
            (TileType.FOREST, spec.forest_count),
        ]
        if not assign_tiles_with_backtracking(grid, cell_order, quotas, spec, rng):
            continue

        tile_map = build_tile_map(
            layout=layout_from_grid(grid),
            player_spawn=spec.player_spawn,
            enemy_spawns=spec.enemy_spawns,
            eagle_position=spec.eagle_position,
        )
        if generated_map_is_valid(tile_map):
            return tile_map

    raise RuntimeError("Failed to generate a valid CSP map within the retry limit")


def assign_tiles_with_backtracking(
    grid: list[list[TileType]],
    cells: list[tuple[int, int]],
    quotas: list[tuple[TileType, int]],
    spec: GeneratorSpec,
    rng: random.Random,
) -> bool:
    """Assign tile types to candidate cells while preserving playability checks."""
    items = [tile for tile, count in quotas for _ in range(count)]
    rng.shuffle(items)

    for tile_type in items:
        placed = False
        for cell in ordered_candidates_for_tile(grid, cells, tile_type, rng):
            x, y = cell
            if grid[y][x] is not TileType.EMPTY:
                continue
            if not placement_is_locally_valid(grid, cell, tile_type, spec):
                continue
            grid[y][x] = tile_type
            if forward_check_reachability(grid, spec):
                placed = True
                break
            grid[y][x] = TileType.EMPTY
        if not placed:
            return False
    return True


def ordered_candidates_for_tile(
    grid: list[list[TileType]],
    cells: list[tuple[int, int]],
    tile_type: TileType,
    rng: random.Random,
) -> list[tuple[int, int]]:
    candidates = list(cells)
    rng.shuffle(candidates)
    if tile_type is TileType.FOREST:
        return candidates
    return sorted(candidates, key=lambda cell: neighbor_block_count(grid, cell), reverse=True)


def placement_is_locally_valid(
    grid: list[list[TileType]],
    cell: tuple[int, int],
    tile_type: TileType,
    spec: GeneratorSpec,
) -> bool:
    x, y = cell
    ex, ey = spec.eagle_position
    if abs(x - ex) <= 1 and abs(y - ey) <= 1:
        return False

    if tile_type in {TileType.STEEL, TileType.WATER} and creates_solid_two_by_two(grid, cell):
        return False

    if tile_type is TileType.WATER and count_adjacent_of_type(grid, cell, TileType.WATER) > 1:
        return False

    return True


def creates_solid_two_by_two(grid: list[list[TileType]], cell: tuple[int, int]) -> bool:
    x, y = cell
    for ox in (0, -1):
        for oy in (0, -1):
            points = [(x + ox, y + oy), (x + ox + 1, y + oy), (x + ox, y + oy + 1), (x + ox + 1, y + oy + 1)]
            if any(px < 0 or py < 0 or py >= len(grid) or px >= len(grid[0]) for px, py in points):
                continue
            occupied = 0
            for px, py in points:
                if (px, py) == cell or grid[py][px] in {TileType.BRICK, TileType.STEEL, TileType.WATER}:
                    occupied += 1
            if occupied == 4:
                return True
    return False


def count_adjacent_of_type(grid: list[list[TileType]], cell: tuple[int, int], tile_type: TileType) -> int:
    x, y = cell
    count = 0
    for nx, ny in orthogonal_neighbors((x, y), len(grid[0]), len(grid)):
        if grid[ny][nx] is tile_type:
            count += 1
    return count


def neighbor_block_count(grid: list[list[TileType]], cell: tuple[int, int]) -> int:
    x, y = cell
    count = 0
    for nx, ny in orthogonal_neighbors((x, y), len(grid[0]), len(grid)):
        if grid[ny][nx] in {TileType.BRICK, TileType.STEEL, TileType.WATER}:
            count += 1
    return count


def forward_check_reachability(grid: list[list[TileType]], spec: GeneratorSpec) -> bool:
    """Reject placements that seal the eagle from all spawns."""
    passable = {
        TileType.EMPTY,
        TileType.FOREST,
    }
    goals = eagle_adjacent_goal_tiles(spec)
    if not goals:
        return False
    for start in (spec.player_spawn, *spec.enemy_spawns):
        if not has_path(grid, start, goals, passable):
            return False
    return True


def generated_map_is_valid(tile_map: TileMap) -> bool:
    goals = {
        tile
        for tile in orthogonal_neighbors(tile_map.eagle_position, tile_map.width, tile_map.height)
        if is_passable_for_tanks(tile_map.tile_at(*tile))
    }
    if not goals:
        return False
    if not eagle_is_protected(tile_map):
        return False
    for start in (tile_map.player_spawn, *tile_map.enemy_spawns):
        if not tile_map_has_path(tile_map, start, goals):
            return False
    return True


def eagle_is_protected(tile_map: TileMap) -> bool:
    ex, ey = tile_map.eagle_position
    neighbors = {
        (ex - 1, ey),
        (ex + 1, ey),
        (ex, ey + 1),
    }
    return all(
        0 <= x < tile_map.width
        and 0 <= y < tile_map.height
        and tile_map.tile_at(x, y) in {TileType.BRICK, TileType.STEEL}
        for x, y in neighbors
    )


def tile_map_has_path(
    tile_map: TileMap,
    start: tuple[int, int],
    goals: set[tuple[int, int]],
) -> bool:
    passable = {TileType.EMPTY, TileType.FOREST}
    queue = deque([start])
    seen = {start}
    while queue:
        x, y = queue.popleft()
        if (x, y) in goals:
            return True
        for nx, ny in orthogonal_neighbors((x, y), tile_map.width, tile_map.height):
            if (nx, ny) in seen:
                continue
            if tile_map.tile_at(nx, ny) not in passable:
                continue
            seen.add((nx, ny))
            queue.append((nx, ny))
    return False


def has_path(
    grid: list[list[TileType]],
    start: tuple[int, int],
    goals: set[tuple[int, int]],
    passable: set[TileType],
) -> bool:
    queue = deque([start])
    seen = {start}
    width = len(grid[0])
    height = len(grid)
    while queue:
        x, y = queue.popleft()
        if (x, y) in goals:
            return True
        for nx, ny in orthogonal_neighbors((x, y), width, height):
            if (nx, ny) in seen:
                continue
            if grid[ny][nx] not in passable:
                continue
            seen.add((nx, ny))
            queue.append((nx, ny))
    return False


def layout_from_grid(grid: list[list[TileType]]) -> list[str]:
    return ["".join(TILE_SYMBOL_BY_TYPE[cell] for cell in row) for row in grid]


def reserved_tiles(spec: GeneratorSpec) -> set[tuple[int, int]]:
    reserved = {spec.player_spawn, spec.eagle_position, *spec.enemy_spawns}
    reserved.update(orthogonal_neighbors(spec.player_spawn, spec.width, spec.height))
    for spawn in spec.enemy_spawns:
        reserved.update(orthogonal_neighbors(spawn, spec.width, spec.height))
    return reserved


def protected_corridor_tiles(spec: GeneratorSpec) -> set[tuple[int, int]]:
    """Keep a guaranteed open corridor from the player and top spawns to the eagle row."""
    px, py = spec.player_spawn
    ex, ey = spec.eagle_position
    corridor = {(px, y) for y in range(ey, py + 1)}
    corridor.update({(x, ey - 2) for x in range(min(px, ex), max(px, ex) + 1)})
    for sx, sy in spec.enemy_spawns:
        corridor.update({(sx, y) for y in range(sy, ey - 2 + 1)})
        corridor.update({(x, ey - 2) for x in range(min(sx, ex), max(sx, ex) + 1)})
    return {
        (x, y)
        for x, y in corridor
        if 0 <= x < spec.width and 0 <= y < spec.height
    }


def eagle_adjacent_goal_tiles(spec: GeneratorSpec) -> set[tuple[int, int]]:
    return {
        tile
        for tile in orthogonal_neighbors(spec.eagle_position, spec.width, spec.height)
        if tile not in {
            (spec.eagle_position[0] - 1, spec.eagle_position[1]),
            (spec.eagle_position[0] + 1, spec.eagle_position[1]),
            (spec.eagle_position[0], spec.eagle_position[1] + 1),
        }
    } | {
        tile
        for tile in orthogonal_neighbors(spec.eagle_position, spec.width, spec.height)
        if tile[1] == spec.eagle_position[1] - 1
    }


def shuffled_candidate_cells(
    spec: GeneratorSpec,
    rng: random.Random,
    blocked: set[tuple[int, int]],
) -> list[tuple[int, int]]:
    cells = [
        (x, y)
        for y in range(spec.height)
        for x in range(spec.width)
        if (x, y) not in blocked
    ]
    rng.shuffle(cells)
    return cells


def _protect_eagle(
    grid: list[list[TileType]],
    spec: GeneratorSpec,
    rng: random.Random,
) -> dict[TileType, int]:
    ex, ey = spec.eagle_position
    fort_tiles = [
        (ex - 1, ey),
        (ex + 1, ey),
        (ex, ey + 1),
    ]
    counts = {TileType.BRICK: 0, TileType.STEEL: 0}
    for cell in fort_tiles:
        x, y = cell
        if 0 <= x < spec.width and 0 <= y < spec.height:
            tile_type = TileType.BRICK if rng.random() < 0.75 else TileType.STEEL
            grid[y][x] = tile_type
            counts[tile_type] += 1
    return counts


def count_tiles(tile_map: TileMap) -> dict[TileType, int]:
    counts = {tile_type: 0 for tile_type in TileType}
    for row in tile_map.tiles:
        for tile_type in row:
            counts[tile_type] += 1
    return counts


def orthogonal_neighbors(
    tile: tuple[int, int],
    width: int,
    height: int,
) -> list[tuple[int, int]]:
    x, y = tile
    neighbors: list[tuple[int, int]] = []
    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
        if 0 <= nx < width and 0 <= ny < height:
            neighbors.append((nx, ny))
    return neighbors
