"""Level construction and progression helpers."""

from __future__ import annotations

from config.levels import (
    BOSS_ENEMY_POOL,
    STARTER_ENEMY_POOL,
    STEEL_FORTRESS_ENEMY_POOL,
)
from game.core.state import GameState, MatchOutcome, UISettings
from game.entities.player import spawn_player
from game.world.map_loader import load_boss_level, load_starter_level, load_steel_fortress_level


LEVEL_1_LABEL = "Level 1: Brick Maze"
LEVEL_2_LABEL = "Level 2: Steel Fortress"
BOSS_LABEL = "Boss Arena"
STANDARD_PROGRESS_LEVELS = {"starter", "steel_fortress"}


def create_starter_game_state() -> GameState:
    return create_game_state_from_settings(UISettings())


def create_game_state_from_settings(settings: UISettings) -> GameState:
    """Create a fresh playable match based on current menu settings."""
    if settings.selected_level == LEVEL_2_LABEL:
        tile_map = load_steel_fortress_level()
        enemy_pool = build_enemy_pool(STEEL_FORTRESS_ENEMY_POOL, settings.difficulty)
        level_name = "steel_fortress"
    elif settings.selected_level == BOSS_LABEL:
        tile_map = load_boss_level()
        enemy_pool = list(BOSS_ENEMY_POOL)
        level_name = "boss"
    else:
        tile_map = load_starter_level()
        enemy_pool = build_enemy_pool(STARTER_ENEMY_POOL, settings.difficulty)
        level_name = "starter"

    lives = 4 if settings.difficulty == "Easy" else 3
    if settings.difficulty == "Hard":
        lives = 2

    return GameState(
        tile_map=tile_map,
        player=spawn_player(tile_map.player_spawn),
        enemies_remaining=len(enemy_pool),
        enemy_count_target=len(enemy_pool),
        enemy_spawn_queue=enemy_pool,
        level_name=level_name,
        debug_overlay_enabled=settings.debug_overlay_enabled,
        path_visualization_enabled=settings.path_visualization_enabled,
        difficulty=settings.difficulty,
        lives=lives,
    )


def build_enemy_pool(base_pool: tuple[str, ...], difficulty: str) -> list[str]:
    """Scale queued enemy pressure by difficulty without changing core AI logic."""
    pool = list(base_pool)
    if difficulty == "Easy":
        if "armor" in pool:
            pool.remove("armor")
        elif pool:
            pool.pop()
    elif difficulty == "Hard":
        pool.extend(["fast", "armor"])
    return pool


def advance_to_boss_level(game_state: GameState) -> None:
    tile_map = load_boss_level()
    game_state.tile_map = tile_map
    game_state.player = spawn_player(tile_map.player_spawn)
    game_state.player_bullet = None
    game_state.active_enemies.clear()
    game_state.enemy_spawn_queue = list(BOSS_ENEMY_POOL)
    game_state.next_enemy_id = 1
    game_state.eagle_destroyed = False
    game_state.enemies_remaining = len(BOSS_ENEMY_POOL)
    game_state.enemy_count_target = len(BOSS_ENEMY_POOL)
    game_state.outcome = MatchOutcome.ACTIVE
    game_state.paused = False
    game_state.level_name = "boss"
