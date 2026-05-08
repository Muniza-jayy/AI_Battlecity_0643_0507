"""Core loop tests for Milestone 3."""

from game.core.state import GameState, InputState
from game.core.loop import update_game_state
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


def test_update_game_state_ends_run_when_bullet_hits_eagle() -> None:
    layout = empty_layout()
    layout[2] = replace_char(layout[2], 3, "E")
    tile_map = build_tile_map(layout, (2, 2), ((0, 0),), (3, 2))
    player = spawn_player(tile_map.player_spawn)
    player.facing = Direction.RIGHT
    game_state = GameState(tile_map=tile_map, player=player)

    update_game_state(game_state, InputState(fire_requested=True))

    assert game_state.eagle_destroyed is True
    assert game_state.running is False
