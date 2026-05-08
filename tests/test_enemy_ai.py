"""Enemy AI and spawning tests for Milestone 7."""

from config.levels import STARTER_ENEMY_POOL
from config.settings import GRID_HEIGHT, GRID_WIDTH, TILE_SIZE
from game.ai.bfs_agent import basic_path_to_eagle, choose_basic_direction
from game.ai.line_of_sight import choose_enemy_shot_direction, choose_enemy_shot_target, has_clear_tile_line
from game.core.loop import spawn_waiting_enemies, update_enemies
from game.core.state import GameState
from game.entities.bullet import spawn_bullet_from_tank
from game.entities.enemy import move_enemy, spawn_enemy, try_spawn_enemy, update_basic_enemy_decision
from game.entities.player import spawn_player
from game.entities.tank import Direction
from game.world.map_loader import build_tile_map, load_starter_level
from game.world.tiles import TileType, is_passable_for_tanks


def empty_layout() -> list[str]:
    return ["." * GRID_WIDTH for _ in range(GRID_HEIGHT)]


def replace_char(source: str, index: int, value: str) -> str:
    return source[:index] + value + source[index + 1 :]


def test_basic_enemy_bfs_heads_toward_eagle_lane() -> None:
    layout = empty_layout()
    layout[5] = replace_char(layout[5], 5, "E")
    tile_map = build_tile_map(layout, (2, 10), ((0, 0),), (5, 5))
    enemy = spawn_enemy(1, "basic", (0, 0))

    direction = choose_basic_direction(tile_map, enemy, tile_map.eagle_position)

    assert direction in {Direction.RIGHT, Direction.DOWN}


def test_basic_enemy_bfs_finds_path_from_all_starter_spawns() -> None:
    starter_level = load_starter_level()
    for enemy_id, spawn in enumerate(starter_level.enemy_spawns, start=1):
        enemy = spawn_enemy(enemy_id, "basic", spawn)
        path = basic_path_to_eagle(starter_level, enemy, starter_level.eagle_position)
        assert len(path) > 1
        assert path[0] == spawn


def test_basic_enemy_bfs_finds_path_on_open_map() -> None:
    layout = empty_layout()
    layout[10] = replace_char(layout[10], 10, "E")
    spawns = ((0, 0), (12, 0), (25, 0))
    tile_map = build_tile_map(layout, (12, 12), spawns, (10, 10))

    for enemy_id, spawn in enumerate(spawns, start=1):
        enemy = spawn_enemy(enemy_id, "basic", spawn)
        path = basic_path_to_eagle(tile_map, enemy, tile_map.eagle_position)
        assert len(path) > 1
        assert path[0] == spawn


def test_line_of_sight_requires_clear_row_or_column() -> None:
    layout = empty_layout()
    layout[2] = replace_char(layout[2], 5, "E")
    tile_map = build_tile_map(layout, (2, 2), ((0, 2),), (5, 2))

    assert has_clear_tile_line(tile_map, (0, 2), (5, 2)) is True

    layout[2] = replace_char(layout[2], 3, "B")
    blocked_map = build_tile_map(layout, (2, 2), ((0, 2),), (5, 2))
    assert has_clear_tile_line(blocked_map, (0, 2), (5, 2)) is False


def test_passable_tiles_match_tank_movement_rules() -> None:
    assert is_passable_for_tanks(TileType.EMPTY) is True
    assert is_passable_for_tanks(TileType.FOREST) is True
    assert is_passable_for_tanks(TileType.BRICK) is False
    assert is_passable_for_tanks(TileType.STEEL) is False
    assert is_passable_for_tanks(TileType.WATER) is False
    assert is_passable_for_tanks(TileType.EAGLE) is False


def test_enemy_prefers_shot_on_eagle_when_visible() -> None:
    layout = empty_layout()
    layout[2] = replace_char(layout[2], 5, "E")
    tile_map = build_tile_map(layout, (2, 10), ((0, 2),), (5, 2))
    enemy = spawn_enemy(1, "basic", (0, 2))
    player = spawn_player((0, 10))

    target = choose_enemy_shot_target(tile_map, enemy, player, tile_map.eagle_position)

    assert target == "eagle"


def test_enemy_shot_direction_points_toward_visible_target() -> None:
    layout = empty_layout()
    layout[2] = replace_char(layout[2], 8, "E")
    tile_map = build_tile_map(layout, (5, 2), ((0, 2),), (8, 2))
    enemy = spawn_enemy(1, "basic", (2, 2))
    player = spawn_player((5, 10))

    direction = choose_enemy_shot_direction(tile_map, enemy, player, tile_map.eagle_position)

    assert direction is Direction.RIGHT


def test_spawn_waiting_enemies_uses_spawn_points_and_pool() -> None:
    layout = empty_layout()
    layout[5] = replace_char(layout[5], 5, "E")
    tile_map = build_tile_map(layout, (12, 12), ((0, 0), (5, 0), (10, 0)), (5, 5))
    game_state = GameState(
        tile_map=tile_map,
        player=spawn_player(tile_map.player_spawn),
        enemies_remaining=len(STARTER_ENEMY_POOL),
        enemy_count_target=len(STARTER_ENEMY_POOL),
        enemy_spawn_queue=list(STARTER_ENEMY_POOL),
    )

    spawn_waiting_enemies(game_state)

    assert len(game_state.active_enemies) == 3
    assert len(game_state.enemy_spawn_queue) == len(STARTER_ENEMY_POOL) - 3


def test_enemy_does_not_spawn_inside_blocked_tile() -> None:
    layout = empty_layout()
    layout[0] = replace_char(layout[0], 0, "B")
    layout[5] = replace_char(layout[5], 5, "E")
    tile_map = build_tile_map(layout, (12, 12), ((0, 0),), (5, 5))

    enemy = try_spawn_enemy(1, "basic", (0, 0), tile_map, blocking_tanks=())

    assert enemy is None


def test_enemy_decision_can_fire_visible_bullet() -> None:
    layout = empty_layout()
    layout[2] = replace_char(layout[2], 5, "E")
    tile_map = build_tile_map(layout, (0, 10), ((0, 2),), (5, 2))
    enemy = spawn_enemy(1, "basic", (0, 2))
    enemy.facing = Direction.RIGHT
    enemy.frames_until_decision = 0
    game_state = GameState(
        tile_map=tile_map,
        player=spawn_player(tile_map.player_spawn),
        active_enemies=[enemy],
        enemies_remaining=1,
        enemy_count_target=1,
    )

    update_enemies(game_state)

    assert enemy.bullet is not None


def test_enemy_aims_before_firing_visible_shot() -> None:
    layout = empty_layout()
    layout[8] = replace_char(layout[8], 15, "E")
    tile_map = build_tile_map(layout, (15, 15), ((5, 8),), (15, 8))
    enemy = spawn_enemy(1, "basic", (5, 8))
    enemy.facing = Direction.DOWN
    player = spawn_player((15, 15))

    should_fire = update_basic_enemy_decision(enemy, tile_map, player)

    assert should_fire is True
    assert enemy.facing is Direction.RIGHT


def test_enemy_bullet_can_hit_player_and_reduce_lives() -> None:
    layout = empty_layout()
    layout[10] = replace_char(layout[10], 20, "E")
    tile_map = build_tile_map(layout, (5, 10), ((0, 10),), (20, 10))
    enemy = spawn_enemy(1, "basic", (0, 10))
    enemy.facing = Direction.RIGHT
    enemy.bullet = spawn_bullet_from_tank(enemy, owner="enemy", owner_id=enemy.enemy_id)
    game_state = GameState(
        tile_map=tile_map,
        player=spawn_player(tile_map.player_spawn),
        active_enemies=[enemy],
        lives=3,
        enemies_remaining=1,
        enemy_count_target=1,
    )
    game_state.player.x = 5 * TILE_SIZE + TILE_SIZE / 2
    game_state.player.y = 10 * TILE_SIZE + TILE_SIZE / 2

    for _ in range(20):
        update_enemies(game_state)
        if game_state.lives < 3:
            break

    assert game_state.lives == 2


def test_enemy_bullet_does_not_hit_off_axis_player_when_shooting_past() -> None:
    layout = empty_layout()
    layout[8] = replace_char(layout[8], 15, "E")
    tile_map = build_tile_map(layout, (15, 10), ((5, 8),), (15, 8))
    enemy = spawn_enemy(1, "basic", (5, 8))
    enemy.facing = Direction.RIGHT
    enemy.bullet = spawn_bullet_from_tank(enemy, owner="enemy", owner_id=enemy.enemy_id)
    game_state = GameState(
        tile_map=tile_map,
        player=spawn_player(tile_map.player_spawn),
        active_enemies=[enemy],
        lives=3,
        enemies_remaining=1,
        enemy_count_target=1,
    )
    # Player is nearby but not on the bullet lane.
    game_state.player.x = 6 * TILE_SIZE + TILE_SIZE / 2
    game_state.player.y = 9 * TILE_SIZE + TILE_SIZE / 2

    for _ in range(10):
        update_enemies(game_state)

    assert game_state.lives == 3


def test_enemy_replans_after_being_stuck_for_several_ticks() -> None:
    layout = empty_layout()
    layout[2] = replace_char(layout[2], 5, "E")
    tile_map = build_tile_map(layout, (12, 12), ((0, 2),), (5, 2))
    enemy = spawn_enemy(1, "basic", (0, 2))
    enemy.debug_path = [(0, 2), (1, 2), (2, 2)]
    enemy.desired_direction = Direction.RIGHT
    enemy.frames_until_decision = 5
    blocker = spawn_player((1, 2))

    for _ in range(20):
        move_enemy(enemy, tile_map, blocking_tanks=(blocker,))

    assert enemy.frames_until_decision == 0


def test_enemy_decision_stores_debug_bfs_path() -> None:
    layout = empty_layout()
    layout[5] = replace_char(layout[5], 5, "E")
    tile_map = build_tile_map(layout, (12, 12), ((0, 0),), (5, 5))
    enemy = spawn_enemy(1, "basic", (0, 0))
    player = spawn_player((12, 12))

    update_basic_enemy_decision(enemy, tile_map, player)

    assert len(enemy.debug_path) > 1
    assert enemy.debug_path[0] == (0, 0)


def test_rightmost_starter_enemy_leaves_top_spawn_lane() -> None:
    from config.levels import STARTER_ENEMY_POOL
    from game.core.loop import spawn_waiting_enemies, update_enemies
    from game.world.map_loader import load_starter_level

    tile_map = load_starter_level()
    game_state = GameState(
        tile_map=tile_map,
        player=spawn_player(tile_map.player_spawn),
        enemies_remaining=len(STARTER_ENEMY_POOL),
        enemy_count_target=len(STARTER_ENEMY_POOL),
        enemy_spawn_queue=list(STARTER_ENEMY_POOL),
    )

    spawn_waiting_enemies(game_state)
    rightmost = max(game_state.active_enemies, key=lambda enemy: enemy.x)

    for _ in range(260):
        update_enemies(game_state)

    assert rightmost.y > TILE_SIZE / 2
