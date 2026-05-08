"""Level construction and progression helpers."""

from __future__ import annotations

from config.levels import BOSS_ENEMY_POOL, STARTER_ENEMY_POOL
from game.core.state import GameState, MatchOutcome
from game.entities.player import spawn_player
from game.world.map_loader import load_boss_level, load_starter_level


def create_starter_game_state() -> GameState:
    tile_map = load_starter_level()
    return GameState(
        tile_map=tile_map,
        player=spawn_player(tile_map.player_spawn),
        enemies_remaining=len(STARTER_ENEMY_POOL),
        enemy_count_target=len(STARTER_ENEMY_POOL),
        enemy_spawn_queue=list(STARTER_ENEMY_POOL),
        level_name="starter",
    )


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
