"""Enemy tank state and behavior helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Sequence

from config.balance import (
    ARMOR_ENEMY_DECISION_INTERVAL,
    ARMOR_ENEMY_HIT_POINTS,
    ARMOR_ENEMY_RETREAT_DECISION_INTERVAL,
    ARMOR_ENEMY_RETREAT_THRESHOLD,
    ARMOR_ENEMY_SPEED,
    BASIC_ENEMY_STUCK_TICKS,
    BOSS_ENEMY_DECISION_INTERVAL,
    BOSS_ENEMY_HIT_POINTS,
    BOSS_ENEMY_SPEED,
    ENEMY_DECISION_INTERVAL,
    ENEMY_SPEED,
    FAST_ENEMY_DECISION_INTERVAL,
    FAST_ENEMY_SPEED,
    TANK_SIZE,
)
from config.settings import TILE_SIZE
from game.ai.astar_agent import astar_path_to_eagle
from game.ai.bfs_agent import basic_path_to_eagle, current_tile
from game.ai.greedy_agent import greedy_path_to_eagle
from game.ai.line_of_sight import choose_enemy_shot_direction
from game.ai.minimax_agent import BossDecision, choose_boss_action
from game.entities.bullet import Bullet, spawn_bullet_from_tank
from game.entities.player import move_tank
from game.entities.tank import Direction, Tank
from game.world.collision import tank_can_occupy
from game.world.tiles import TileMap


@dataclass
class EnemyTank(Tank):
    """Minimal enemy tank state for the first AI milestone."""

    enemy_id: int
    role: str
    decision_interval: int = ENEMY_DECISION_INTERVAL
    frames_until_decision: int = 0
    desired_direction: Direction | None = None
    bullet: Bullet | None = None
    debug_path: list[tuple[int, int]] = field(default_factory=list)
    stuck_ticks: int = 0
    hit_points: int = 1
    max_hit_points: int = 1
    planned_map_revision: int = -1
    boss_phase: int = 0
    boss_search_depth: int = 0
    nodes_without_pruning: int = 0
    nodes_with_pruning: int = 0
    pruned_nodes: int = 0
    speedup_ratio: float = 1.0


def spawn_enemy(enemy_id: int, role: str, spawn_tile: tuple[int, int]) -> EnemyTank:
    """Create an enemy tank centered on its spawn tile."""
    tile_x, tile_y = spawn_tile
    speed = ENEMY_SPEED
    decision_interval = ENEMY_DECISION_INTERVAL
    hit_points = 1
    if role == "fast":
        speed = FAST_ENEMY_SPEED
        decision_interval = FAST_ENEMY_DECISION_INTERVAL
    elif role == "armor":
        speed = ARMOR_ENEMY_SPEED
        decision_interval = ARMOR_ENEMY_DECISION_INTERVAL
        hit_points = ARMOR_ENEMY_HIT_POINTS
    elif role == "boss":
        speed = BOSS_ENEMY_SPEED
        decision_interval = BOSS_ENEMY_DECISION_INTERVAL
        hit_points = BOSS_ENEMY_HIT_POINTS

    return EnemyTank(
        x=tile_x * TILE_SIZE + TILE_SIZE / 2,
        y=tile_y * TILE_SIZE + TILE_SIZE / 2,
        size=TANK_SIZE,
        speed=speed,
        facing=Direction.DOWN,
        enemy_id=enemy_id,
        role=role,
        decision_interval=decision_interval,
        hit_points=hit_points,
        max_hit_points=hit_points,
    )


def try_spawn_enemy(
    enemy_id: int,
    role: str,
    spawn_tile: tuple[int, int],
    tile_map: TileMap,
    blocking_tanks: Sequence[Tank],
) -> EnemyTank | None:
    """Spawn an enemy only if the spawn tile is currently free."""
    enemy = spawn_enemy(enemy_id, role, spawn_tile)
    if not tank_can_occupy(enemy.x, enemy.y, enemy.size, tile_map, blocking_tanks=blocking_tanks):
        return None
    return enemy


def tick_enemy_decision_timer(enemy: EnemyTank) -> bool:
    """Return whether the enemy should make a fresh decision this frame."""
    if enemy.frames_until_decision <= 0:
        return True
    enemy.frames_until_decision -= 1
    return False


def update_basic_enemy_decision(
    enemy: EnemyTank,
    tile_map: TileMap,
    player: Tank,
    player_lives: int = 1,
) -> bool:
    """Recompute a basic tank plan and return whether it should fire."""
    if enemy.role == "boss":
        return update_boss_enemy_decision(enemy, tile_map, player, player_lives=player_lives)

    enemy.debug_path = plan_path_to_eagle(tile_map, enemy)
    enemy.desired_direction = desired_direction_from_path(enemy)
    shot_direction = choose_enemy_shot_direction(tile_map, enemy, player, tile_map.eagle_position)
    if shot_direction is not None:
        enemy.facing = shot_direction
    if enemy.role == "armor" and enemy.hit_points <= ARMOR_ENEMY_RETREAT_THRESHOLD:
        enemy.frames_until_decision = ARMOR_ENEMY_RETREAT_DECISION_INTERVAL
    else:
        enemy.frames_until_decision = enemy.decision_interval
    enemy.planned_map_revision = tile_map.revision
    return shot_direction is not None


def update_boss_enemy_decision(
    enemy: EnemyTank,
    tile_map: TileMap,
    player: Tank,
    player_lives: int,
) -> bool:
    """Compute a boss action from reduced-state minimax."""
    decision = choose_boss_action(
        tile_map=tile_map,
        boss_tile=current_tile(enemy),
        player_tile=current_tile(player),
        eagle_tile=tile_map.eagle_position,
        boss_hp=enemy.hit_points,
        player_lives=player_lives,
    )
    apply_boss_decision(enemy, decision, tile_map)
    return decision.should_fire


def apply_boss_decision(enemy: EnemyTank, decision: BossDecision, tile_map: TileMap) -> None:
    enemy.desired_direction = decision.desired_direction
    if decision.desired_direction is not None:
        enemy.facing = decision.desired_direction
    enemy.frames_until_decision = enemy.decision_interval
    enemy.debug_path = [current_tile(enemy)]
    if enemy.desired_direction is not None:
        enemy.debug_path.append(step_direction(current_tile(enemy), enemy.desired_direction))
    enemy.boss_search_depth = decision.search_depth
    enemy.nodes_without_pruning = decision.nodes_without_pruning
    enemy.nodes_with_pruning = decision.nodes_with_pruning
    enemy.pruned_nodes = decision.pruned_nodes
    enemy.speedup_ratio = decision.speedup_ratio
    enemy.boss_phase = boss_phase_from_hp(enemy.hit_points)
    enemy.planned_map_revision = tile_map.revision


def boss_phase_from_hp(hit_points: int) -> int:
    if hit_points > 6:
        return 1
    if hit_points > 3:
        return 2
    return 3


def plan_path_to_eagle(tile_map: TileMap, enemy: EnemyTank) -> list[tuple[int, int]]:
    """Dispatch to the path planner that matches the enemy role."""
    if enemy.role == "fast":
        return greedy_path_to_eagle(tile_map, enemy, tile_map.eagle_position)
    if enemy.role == "armor":
        return astar_path_to_eagle(tile_map, enemy, tile_map.eagle_position)
    return basic_path_to_eagle(tile_map, enemy, tile_map.eagle_position)


def enemy_requires_replan(enemy: EnemyTank, tile_map: TileMap) -> bool:
    """Return whether the current stored plan is stale against the live map."""
    return enemy.planned_map_revision != tile_map.revision


def move_enemy(enemy: EnemyTank, tile_map: TileMap, blocking_tanks: Sequence[Tank]) -> bool:
    """Apply the current movement plan to the enemy tank and report whether it moved."""
    sync_enemy_path(enemy)
    before = (enemy.x, enemy.y)
    move_tank(enemy, enemy.desired_direction, tile_map, blocking_tanks=tuple(blocking_tanks))
    moved = (enemy.x, enemy.y) != before
    if enemy.desired_direction is not None:
        if moved:
            enemy.stuck_ticks = 0
        else:
            enemy.stuck_ticks += 1
            if enemy.stuck_ticks >= BASIC_ENEMY_STUCK_TICKS:
                enemy.frames_until_decision = 0
                enemy.stuck_ticks = 0
    return moved


def sync_enemy_path(enemy: EnemyTank) -> None:
    """Advance the stored BFS path to the current tile and refresh the desired direction."""
    if len(enemy.debug_path) < 2:
        enemy.desired_direction = None
        return

    current = current_tile(enemy)
    if current in enemy.debug_path:
        while len(enemy.debug_path) > 1 and enemy.debug_path[0] != current:
            enemy.debug_path.pop(0)
    enemy.desired_direction = desired_direction_from_path(enemy)


def desired_direction_from_path(enemy: EnemyTank) -> Direction | None:
    """Convert the first BFS path step into a movement direction."""
    if len(enemy.debug_path) < 2:
        return None

    start_x, start_y = enemy.debug_path[0]
    next_x, next_y = enemy.debug_path[1]
    dx = next_x - start_x
    dy = next_y - start_y
    if dx > 0:
        return Direction.RIGHT
    if dx < 0:
        return Direction.LEFT
    if dy > 0:
        return Direction.DOWN
    if dy < 0:
        return Direction.UP
    return None


def fire_enemy_bullet(enemy: EnemyTank) -> None:
    """Fire an enemy bullet if one is not already active."""
    if enemy.bullet is None:
        enemy.bullet = spawn_bullet_from_tank(enemy, owner="enemy", owner_id=enemy.enemy_id)


def step_direction(tile: tuple[int, int], direction: Direction) -> tuple[int, int]:
    if direction is Direction.UP:
        return (tile[0], tile[1] - 1)
    if direction is Direction.DOWN:
        return (tile[0], tile[1] + 1)
    if direction is Direction.LEFT:
        return (tile[0] - 1, tile[1])
    return (tile[0] + 1, tile[1])
