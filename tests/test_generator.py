"""CSP map generator and simulation-mode tests for Milestone 10."""

from config.levels import STARTER_ENEMY_POOL
from config.settings import GRID_HEIGHT, GRID_WIDTH
from game.core.loop import update_game_state
from game.core.state import GameState, InputState, MatchOutcome
from game.entities.player import spawn_player
from game.modes.simulation_mode import regenerate_simulation_level
from game.world.map_generator import count_tiles, eagle_is_protected, generate_csp_map, generated_map_is_valid, GeneratorSpec
from game.world.map_loader import load_starter_level
from game.world.tiles import TileType


def test_generate_csp_map_matches_standard_dimensions() -> None:
    tile_map = generate_csp_map(seed=1234)

    assert tile_map.width == GRID_WIDTH
    assert tile_map.height == GRID_HEIGHT
    assert len(tile_map.tiles) == GRID_HEIGHT


def test_generated_map_enforces_eagle_protection_and_reachability() -> None:
    tile_map = generate_csp_map(seed=4321)

    assert eagle_is_protected(tile_map) is True
    assert generated_map_is_valid(tile_map) is True


def test_regenerate_simulation_level_replaces_match_with_generated_map() -> None:
    tile_map = load_starter_level()
    game_state = GameState(
        tile_map=tile_map,
        player=spawn_player(tile_map.player_spawn),
        enemies_remaining=len(STARTER_ENEMY_POOL),
        enemy_count_target=len(STARTER_ENEMY_POOL),
        enemy_spawn_queue=list(STARTER_ENEMY_POOL),
        level_name="starter",
    )

    regenerate_simulation_level(game_state, seed=99)

    assert game_state.level_name == "simulation"
    assert game_state.generated_seed == 99
    assert generated_map_is_valid(game_state.tile_map) is True
    assert game_state.enemies_remaining == len(STARTER_ENEMY_POOL)
    assert game_state.lives == 3


def test_update_game_state_toggles_debug_overlay() -> None:
    tile_map = load_starter_level()
    game_state = GameState(tile_map=tile_map, player=spawn_player(tile_map.player_spawn))

    update_game_state(game_state, InputState(toggle_debug_overlay_requested=True))

    assert game_state.debug_overlay_enabled is True


def test_update_game_state_regenerates_into_simulation_mode() -> None:
    tile_map = load_starter_level()
    game_state = GameState(
        tile_map=tile_map,
        player=spawn_player(tile_map.player_spawn),
        enemies_remaining=len(STARTER_ENEMY_POOL),
        enemy_count_target=len(STARTER_ENEMY_POOL),
        enemy_spawn_queue=list(STARTER_ENEMY_POOL),
        outcome=MatchOutcome.VICTORY,
    )

    update_game_state(game_state, InputState(regenerate_map_requested=True))

    assert game_state.level_name == "simulation"
    assert generated_map_is_valid(game_state.tile_map) is True
    assert game_state.outcome is MatchOutcome.ACTIVE


def test_regenerate_simulation_level_recovers_from_zero_lives() -> None:
    tile_map = load_starter_level()
    game_state = GameState(
        tile_map=tile_map,
        player=spawn_player(tile_map.player_spawn),
        lives=0,
        outcome=MatchOutcome.DEFEAT,
    )

    regenerate_simulation_level(game_state, seed=77)

    assert game_state.lives == 3
    assert game_state.outcome is MatchOutcome.ACTIVE


def test_generate_csp_map_honors_requested_tile_quotas() -> None:
    spec = GeneratorSpec(brick_count=20, steel_count=10, water_count=8, forest_count=6)
    tile_map = generate_csp_map(seed=2024, spec=spec)
    counts = count_tiles(tile_map)

    assert counts[TileType.BRICK] == spec.brick_count
    assert counts[TileType.STEEL] == spec.steel_count
    assert counts[TileType.WATER] == spec.water_count
    assert counts[TileType.FOREST] == spec.forest_count
