"""Core state models for the early gameplay loop."""

from __future__ import annotations

from dataclasses import dataclass

from game.entities.bullet import Bullet
from game.entities.tank import Direction, Tank
from game.world.tiles import TileMap


@dataclass
class InputState:
    """Input gathered for a single frame."""

    quit_requested: bool = False
    toggle_pause_requested: bool = False
    resized_to: tuple[int, int] | None = None
    movement_direction: Direction | None = None
    fire_requested: bool = False


@dataclass
class GameState:
    """Minimal runtime state for Milestone 3."""

    tile_map: TileMap
    player: Tank
    player_bullet: Bullet | None = None
    eagle_destroyed: bool = False
    paused: bool = False
    running: bool = True
    frame_count: int = 0
