"""Load fixed tile maps from simple level data."""

from __future__ import annotations

from config.levels import (
    BOSS_EAGLE_POSITION,
    BOSS_ENEMY_SPAWNS,
    BOSS_LEVEL_LAYOUT,
    BOSS_PLAYER_SPAWN,
    EAGLE_POSITION,
    ENEMY_SPAWNS,
    PLAYER_SPAWN,
    STEEL_FORTRESS_EAGLE_POSITION,
    STEEL_FORTRESS_ENEMY_SPAWNS,
    STEEL_FORTRESS_LAYOUT,
    STEEL_FORTRESS_PLAYER_SPAWN,
    STARTER_LEVEL_LAYOUT,
)
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
    if not layout:
        raise ValueError("Level layout must contain at least one row")
    width = len(layout[0])
    if any(len(row) != width for row in layout):
        raise ValueError("Level rows must all have the same width")
    height = len(layout)

    tiles = tuple(
        tuple(TILE_SYMBOLS[symbol] for symbol in row)
        for row in layout
    )
    return TileMap(
        width=width,
        height=height,
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


def load_steel_fortress_level() -> TileMap:
    """Return the fixed steel-heavy standard arena."""
    return build_tile_map(
        layout=STEEL_FORTRESS_LAYOUT,
        player_spawn=STEEL_FORTRESS_PLAYER_SPAWN,
        enemy_spawns=STEEL_FORTRESS_ENEMY_SPAWNS,
        eagle_position=STEEL_FORTRESS_EAGLE_POSITION,
    )


def load_boss_level() -> TileMap:
    """Return the fixed 12x12 boss arena."""
    return build_tile_map(
        layout=BOSS_LEVEL_LAYOUT,
        player_spawn=BOSS_PLAYER_SPAWN,
        enemy_spawns=BOSS_ENEMY_SPAWNS,
        eagle_position=BOSS_EAGLE_POSITION,
    )
