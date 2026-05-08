"""Generated-map simulation/debug mode helpers."""

from __future__ import annotations

from config.levels import STARTER_ENEMY_POOL
from game.core.state import GameState, MatchOutcome
from game.entities.player import spawn_player
from game.world.map_generator import generate_csp_map


def regenerate_simulation_level(game_state: GameState, seed: int | None = None) -> None:
    """Replace the current match with a generated CSP standard arena."""
    tile_map = generate_csp_map(seed=seed)
    game_state.tile_map = tile_map
    game_state.player = spawn_player(tile_map.player_spawn)
    game_state.player_bullet = None
    game_state.active_enemies.clear()
    game_state.enemy_spawn_queue = list(STARTER_ENEMY_POOL)
    game_state.next_enemy_id = 1
    game_state.eagle_destroyed = False
    game_state.lives = 3
    game_state.enemies_remaining = len(STARTER_ENEMY_POOL)
    game_state.enemy_count_target = len(STARTER_ENEMY_POOL)
    game_state.outcome = MatchOutcome.ACTIVE
    game_state.paused = False
    game_state.level_name = "simulation"
    game_state.generated_seed = seed
