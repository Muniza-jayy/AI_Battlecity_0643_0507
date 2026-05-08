"""Boss arena and minimax behavior tests for Milestone 9."""

from game.ai.minimax_agent import boss_phase_depth, choose_boss_action
from game.core.state import GameState
from game.entities.enemy import boss_phase_from_hp, spawn_enemy, update_basic_enemy_decision
from game.entities.player import spawn_player
from game.world.map_loader import build_tile_map, load_boss_level


def test_boss_spawn_uses_expected_stats() -> None:
    tile_map = load_boss_level()
    boss = spawn_enemy(1, "boss", tile_map.enemy_spawns[0])

    assert boss.role == "boss"
    assert boss.hit_points == 10
    assert boss.max_hit_points == 10
    assert boss.decision_interval == 10


def test_boss_phase_depth_matches_prd_thresholds() -> None:
    assert boss_phase_depth(10) == 2
    assert boss_phase_depth(6) == 3
    assert boss_phase_depth(3) == 4
    assert boss_phase_from_hp(10) == 1
    assert boss_phase_from_hp(6) == 2
    assert boss_phase_from_hp(3) == 3


def test_boss_minimax_records_alpha_beta_metrics() -> None:
    tile_map = load_boss_level()
    boss = spawn_enemy(1, "boss", tile_map.enemy_spawns[0])
    player = spawn_player(tile_map.player_spawn)

    should_fire = update_basic_enemy_decision(boss, tile_map, player, player_lives=3)

    assert boss.boss_search_depth == 2
    assert boss.nodes_without_pruning >= boss.nodes_with_pruning > 0
    assert boss.speedup_ratio >= 1.0
    assert boss.pruned_nodes >= 0
    assert isinstance(should_fire, bool)


def test_boss_minimax_prefers_shot_when_eagle_is_visible() -> None:
    layout = [
        ".....X......".replace("X", "."),
        "............",
        "............",
        "............",
        "............",
        ".....E......".replace("E", "."),
        "............",
        "............",
        "............",
        "............",
        ".....E......",
        ".....P......",
    ]
    tile_map = build_tile_map(layout, (5, 11), ((5, 0),), (5, 10))

    decision = choose_boss_action(
        tile_map=tile_map,
        boss_tile=(5, 0),
        player_tile=(5, 11),
        eagle_tile=(5, 10),
        boss_hp=10,
        player_lives=3,
    )

    assert decision.should_fire is True


def test_boss_level_game_state_can_host_single_boss() -> None:
    tile_map = load_boss_level()
    game_state = GameState(
        tile_map=tile_map,
        player=spawn_player(tile_map.player_spawn),
        enemy_spawn_queue=["boss"],
        enemies_remaining=1,
        enemy_count_target=1,
        level_name="boss",
    )

    assert game_state.tile_map.width == 12
    assert game_state.enemy_spawn_queue == ["boss"]
