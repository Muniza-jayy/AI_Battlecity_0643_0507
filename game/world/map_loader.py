"""Load fixed tile maps from simple level data."""

from __future__ import annotations

from config.levels import EAGLE_POSITION, ENEMY_SPAWNS, PLAYER_SPAWN, STARTER_LEVEL_LAYOUT
from config.settings import GRID_HEIGHT, GRID_WIDTH
from game.world.tiles import TileMap, TileType


TILE_SYMBOLS: dict[str, TileType] = {
    ".": TileType.EMPTY,
    "B": TileType.BRICK,
    "S": TileType.STEEL,
    "W": TileType.WATER,
    "F": TileType.FOREST,
    "E": TileType.EAGLE,
    "P": TileType.EMPTY,
}


def build_tile_map(
    layout: list[str],
    player_spawn: tuple[int, int],
    enemy_spawns: tuple[tuple[int, int], ...],
    eagle_position: tuple[int, int],
) -> TileMap:
    if len(layout) != GRID_HEIGHT:
        raise ValueError(f"Expected {GRID_HEIGHT} rows, received {len(layout)}")
    if any(len(row) != GRID_WIDTH for row in layout):
        raise ValueError("Level rows must match the configured grid width")

    tiles = tuple(
        tuple(TILE_SYMBOLS[symbol] for symbol in row)
        for row in layout
    )
    return TileMap(
        width=GRID_WIDTH,
        height=GRID_HEIGHT,
        tiles=tiles,
        player_spawn=player_spawn,
        enemy_spawns=enemy_spawns,
        eagle_position=eagle_position,
    )


def load_starter_level() -> TileMap:
    """Return the first fixed standard level."""
    return build_tile_map(
        layout=STARTER_LEVEL_LAYOUT,
        player_spawn=PLAYER_SPAWN,
        enemy_spawns=ENEMY_SPAWNS,
        eagle_position=EAGLE_POSITION,
    )
