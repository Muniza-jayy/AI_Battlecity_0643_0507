"""Core loop tests for Milestone 3."""

from config.levels import STARTER_ENEMY_POOL
from game.core.state import GameState, InputState, MatchOutcome
from game.core.loop import evaluate_match_state, update_game_state
from game.entities.player import spawn_player
from game.entities.tank import Direction
from game.world.map_loader import load_starter_level
from game.world.map_loader import build_tile_map
from config.settings import GRID_HEIGHT, GRID_WIDTH


def empty_layout() -> list[str]:
    return ["." * GRID_WIDTH for _ in range(GRID_HEIGHT)]


def replace_char(source: str, index: int, value: str) -> str:
    return source[:index] + value + source[index + 1 :]


def test_update_game_state_toggles_pause() -> None:
    tile_map = load_starter_level()
    game_state = GameState(tile_map=tile_map, player=spawn_player(tile_map.player_spawn))

    update_game_state(game_state, InputState(toggle_pause_requested=True))

    assert game_state.paused is True
    assert game_state.frame_count == 1


def test_update_game_state_advances_frames_when_not_paused() -> None:
    tile_map = load_starter_level()
    game_state = GameState(
        tile_map=tile_map,
        player=spawn_player(tile_map.player_spawn),
        enemies_remaining=len(STARTER_ENEMY_POOL),
        enemy_count_target=len(STARTER_ENEMY_POOL),
    )

    update_game_state(game_state, InputState())

    assert game_state.frame_count == 1
    assert game_state.running is True


def test_update_game_state_honors_quit_request() -> None:
    tile_map = load_starter_level()
    game_state = GameState(tile_map=tile_map, player=spawn_player(tile_map.player_spawn))

    update_game_state(game_state, InputState(quit_requested=True))

    assert game_state.running is False


def test_update_game_state_counts_frames_while_paused() -> None:
    tile_map = load_starter_level()
    game_state = GameState(tile_map=tile_map, player=spawn_player(tile_map.player_spawn), paused=True)

    update_game_state(game_state, InputState())

    assert game_state.paused is True
    assert game_state.frame_count == 1


def test_update_game_state_ends_run_when_bullet_hits_eagle() -> None:
    layout = empty_layout()
    layout[2] = replace_char(layout[2], 3, "E")
    tile_map = build_tile_map(layout, (2, 2), ((0, 0),), (3, 2))
    player = spawn_player(tile_map.player_spawn)
    player.facing = Direction.RIGHT
    game_state = GameState(tile_map=tile_map, player=player)

    update_game_state(game_state, InputState(fire_requested=True))

    assert game_state.eagle_destroyed is True
    assert game_state.running is True
    assert game_state.outcome is MatchOutcome.DEFEAT


def test_evaluate_match_state_defeat_when_lives_reach_zero() -> None:
    tile_map = load_starter_level()
    game_state = GameState(tile_map=tile_map, player=spawn_player(tile_map.player_spawn), lives=0)

    evaluate_match_state(game_state)

    assert game_state.outcome is MatchOutcome.DEFEAT
    assert game_state.running is True


def test_evaluate_match_state_victory_when_all_enemies_cleared() -> None:
    tile_map = load_starter_level()
    game_state = GameState(
        tile_map=tile_map,
        player=spawn_player(tile_map.player_spawn),
        enemy_count_target=3,
        enemies_remaining=0,
    )

    evaluate_match_state(game_state)

    assert game_state.outcome is MatchOutcome.VICTORY
    assert game_state.running is True


def test_evaluate_match_state_does_not_auto_win_without_enemy_target() -> None:
    tile_map = load_starter_level()
    game_state = GameState(tile_map=tile_map, player=spawn_player(tile_map.player_spawn))

    evaluate_match_state(game_state)

    assert game_state.outcome is MatchOutcome.ACTIVE
    assert game_state.running is True


def test_update_game_state_keeps_frozen_outcome_on_screen_until_quit() -> None:
    tile_map = load_starter_level()
    game_state = GameState(
        tile_map=tile_map,
        player=spawn_player(tile_map.player_spawn),
        outcome=MatchOutcome.DEFEAT,
    )

    update_game_state(game_state, InputState())

    assert game_state.outcome is MatchOutcome.DEFEAT
    assert game_state.running is True
    assert game_state.frame_count == 1


def test_update_game_state_quits_from_frozen_outcome_when_requested() -> None:
    tile_map = load_starter_level()
    game_state = GameState(
        tile_map=tile_map,
        player=spawn_player(tile_map.player_spawn),
        outcome=MatchOutcome.VICTORY,
    )

    update_game_state(game_state, InputState(quit_requested=True))

    assert game_state.running is False
