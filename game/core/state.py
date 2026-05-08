"""Core state models for the early gameplay loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from game.entities.bullet import Bullet
from game.entities.enemy import EnemyTank
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


class MatchOutcome(StrEnum):
    ACTIVE = "active"
    VICTORY = "victory"
    DEFEAT = "defeat"


@dataclass
class GameState:
    """Runtime state for the current playable match."""

    tile_map: TileMap
    player: Tank
    player_bullet: Bullet | None = None
    active_enemies: list[EnemyTank] = field(default_factory=list)
    enemy_spawn_queue: list[str] = field(default_factory=list)
    next_enemy_id: int = 1
    eagle_destroyed: bool = False
    lives: int = 3
    score: int = 0
    enemies_remaining: int = 0
    enemy_count_target: int = 0
    level_name: str = "starter"
    outcome: MatchOutcome = MatchOutcome.ACTIVE
    paused: bool = False
    running: bool = True
    frame_count: int = 0
