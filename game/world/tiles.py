"""Tile definitions and map structures for the game world."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TileType(StrEnum):
    EMPTY = "empty"
    BRICK = "brick"
    STEEL = "steel"
    WATER = "water"
    FOREST = "forest"
    EAGLE = "eagle"


@dataclass(frozen=True)
class TileProperties:
    blocks_tanks: bool
    blocks_bullets: bool
    destructible: bool


TILE_PROPERTIES: dict[TileType, TileProperties] = {
    TileType.EMPTY: TileProperties(False, False, False),
    TileType.BRICK: TileProperties(True, True, True),
    TileType.STEEL: TileProperties(True, True, False),
    TileType.WATER: TileProperties(True, False, False),
    TileType.FOREST: TileProperties(False, False, False),
    TileType.EAGLE: TileProperties(True, True, False),
}


@dataclass
class TileMap:
    width: int
    height: int
    tiles: tuple[tuple[TileType, ...], ...]
    player_spawn: tuple[int, int]
    enemy_spawns: tuple[tuple[int, int], ...]
    eagle_position: tuple[int, int]

    def tile_at(self, x: int, y: int) -> TileType:
        return self.tiles[y][x]


def blocks_tanks(tile_type: TileType) -> bool:
    return TILE_PROPERTIES[tile_type].blocks_tanks


def is_passable_for_tanks(tile_type: TileType) -> bool:
    return not TILE_PROPERTIES[tile_type].blocks_tanks


def blocks_bullets(tile_type: TileType) -> bool:
    return TILE_PROPERTIES[tile_type].blocks_bullets


def is_destructible(tile_type: TileType) -> bool:
    return TILE_PROPERTIES[tile_type].destructible
