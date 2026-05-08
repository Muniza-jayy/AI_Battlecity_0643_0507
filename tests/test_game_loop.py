"""Core loop tests for Milestone 3."""

from game.core.state import GameState, InputState
from game.core.loop import update_game_state
from game.entities.player import spawn_player
from game.world.map_loader import load_starter_level


def test_update_game_state_toggles_pause() -> None:
    tile_map = load_starter_level()
    game_state = GameState(tile_map=tile_map, player=spawn_player(tile_map.player_spawn))

    update_game_state(game_state, InputState(toggle_pause_requested=True))

    assert game_state.paused is True
    assert game_state.frame_count == 1


def test_update_game_state_advances_frames_when_not_paused() -> None:
    tile_map = load_starter_level()
    game_state = GameState(tile_map=tile_map, player=spawn_player(tile_map.player_spawn))

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
