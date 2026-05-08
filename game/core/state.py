"""Core state models for the early gameplay loop."""

from __future__ import annotations

from dataclasses import dataclass

from game.world.tiles import TileMap


@dataclass
class InputState:
    """Input gathered for a single frame."""

    quit_requested: bool = False
    toggle_pause_requested: bool = False
    resized_to: tuple[int, int] | None = None


@dataclass
class GameState:
    """Minimal runtime state for Milestone 3."""

    tile_map: TileMap
    paused: bool = False
    running: bool = True
    frame_count: int = 0
