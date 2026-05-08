"""Movement and collision tests for the player tank."""

from config.settings import GRID_HEIGHT, GRID_WIDTH, TILE_SIZE
from game.entities.player import move_player, spawn_player
from game.entities.tank import Direction
from game.world.map_loader import build_tile_map
from game.world.tiles import TileType


def empty_layout() -> list[str]:
    return ["." * GRID_WIDTH for _ in range(GRID_HEIGHT)]


def replace_char(source: str, index: int, value: str) -> str:
    return source[:index] + value + source[index + 1 :]


def test_player_moves_right_on_empty_tiles() -> None:
    layout = empty_layout()
    layout[10] = replace_char(layout[10], 5, "E")
    tile_map = build_tile_map(layout, (2, 2), ((0, 0),), (5, 10))
    player = spawn_player((2, 2))

    move_player(player, Direction.RIGHT, tile_map)

    assert player.x == (2 * TILE_SIZE + TILE_SIZE / 2) + player.speed


def test_player_cannot_move_into_blocking_brick_tile() -> None:
    layout = empty_layout()
    layout[2] = replace_char(layout[2], 3, "B")
    layout[10] = replace_char(layout[10], 5, "E")
    tile_map = build_tile_map(layout, (2, 2), ((0, 0),), (5, 10))
    player = spawn_player((2, 2))
    starting_x = player.x

    move_player(player, Direction.RIGHT, tile_map)
    move_player(player, Direction.RIGHT, tile_map)

    assert player.x == starting_x + player.speed


def test_player_cannot_overlap_eagle_tile() -> None:
    layout = empty_layout()
    layout[2] = replace_char(layout[2], 3, "E")
    tile_map = build_tile_map(layout, (2, 2), ((0, 0),), (3, 2))
    player = spawn_player((2, 2))
    starting_x = player.x

    move_player(player, Direction.RIGHT, tile_map)
    move_player(player, Direction.RIGHT, tile_map)

    assert player.x == starting_x + player.speed


def test_alignment_assist_straightens_vertical_turn_when_near_lane_center() -> None:
    layout = empty_layout()
    layout[10] = replace_char(layout[10], 5, "E")
    tile_map = build_tile_map(layout, (2, 2), ((0, 0),), (5, 10))
    player = spawn_player((2, 2))
    player.x += 4

    move_player(player, Direction.UP, tile_map)

    assert player.x == 2 * TILE_SIZE + TILE_SIZE / 2
    assert player.y == (2 * TILE_SIZE + TILE_SIZE / 2) - player.speed


def test_perpendicular_turn_is_blocked_when_too_far_from_lane_center() -> None:
    layout = empty_layout()
    layout[10] = replace_char(layout[10], 5, "E")
    tile_map = build_tile_map(layout, (2, 2), ((0, 0),), (5, 10))
    player = spawn_player((2, 2))

    move_player(player, Direction.RIGHT, tile_map)
    move_player(player, Direction.RIGHT, tile_map)
    starting_x = player.x
    starting_y = player.y

    move_player(player, Direction.UP, tile_map)

    assert player.x == starting_x - player.speed
    assert player.y == starting_y
