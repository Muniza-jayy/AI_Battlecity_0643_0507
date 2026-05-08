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
    toggle_debug_overlay_requested: bool = False
    regenerate_map_requested: bool = False


class MatchOutcome(StrEnum):
    ACTIVE = "active"
    VICTORY = "victory"
    DEFEAT = "defeat"


class AppScreen(StrEnum):
    WELCOME = "welcome"
    OPTIONS = "options"
    ABOUT = "about"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


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
    debug_overlay_enabled: bool = False
    generated_seed: int | None = None
    outcome: MatchOutcome = MatchOutcome.ACTIVE
    paused: bool = False
    running: bool = True
    frame_count: int = 0


@dataclass
class UISettings:
    """User-facing UI and play configuration."""

    selected_level: str = "Level 1: Brick Maze"
    debug_overlay_enabled: bool = False
    path_visualization_enabled: bool = True
    difficulty: str = "Normal"


@dataclass
class AppState:
    """Top-level application state for screen routing."""

    current_screen: AppScreen = AppScreen.WELCOME
    running: bool = True
    game_state: GameState | None = None
    ui_settings: UISettings = field(default_factory=UISettings)
