"""Boss Tank minimax planning with alpha-beta pruning on a reduced tile-state model."""

from __future__ import annotations

from dataclasses import dataclass
from math import inf

from game.ai.bfs_agent import manhattan_distance, neighbor_tiles
from game.ai.line_of_sight import direction_between, has_clear_tile_line
from game.entities.tank import Direction
from game.world.tiles import TileMap


@dataclass(frozen=True)
class BossDecision:
    """The chosen boss action and associated search metrics."""

    desired_direction: Direction | None
    should_fire: bool
    search_depth: int
    nodes_without_pruning: int
    nodes_with_pruning: int
    pruned_nodes: int
    speedup_ratio: float


@dataclass(frozen=True)
class BossArenaState:
    """Reduced tile-level state for boss search."""

    boss_tile: tuple[int, int]
    player_tile: tuple[int, int]
    eagle_tile: tuple[int, int]
    boss_hp: int
    player_lives: int
    eagle_destroyed: bool = False


def choose_boss_action(
    tile_map: TileMap,
    boss_tile: tuple[int, int],
    player_tile: tuple[int, int],
    eagle_tile: tuple[int, int],
    boss_hp: int,
    player_lives: int,
) -> BossDecision:
    """Choose the boss action with minimax and alpha-beta metrics."""
    depth = boss_phase_depth(boss_hp)
    state = BossArenaState(boss_tile, player_tile, eagle_tile, boss_hp, player_lives)

    plain = _minimax_root(tile_map, state, depth)
    pruned = _alphabeta_root(tile_map, state, depth)
    speedup_ratio = plain["nodes"] / pruned["nodes"] if pruned["nodes"] else 1.0
    return BossDecision(
        desired_direction=pruned["direction"],
        should_fire=pruned["should_fire"],
        search_depth=depth,
        nodes_without_pruning=plain["nodes"],
        nodes_with_pruning=pruned["nodes"],
        pruned_nodes=pruned["pruned"],
        speedup_ratio=speedup_ratio,
    )


def boss_phase_depth(boss_hp: int) -> int:
    """Map boss HP to the PRD-defined search depth phases."""
    if boss_hp > 6:
        return 2
    if boss_hp > 3:
        return 3
    return 4


def _minimax_root(tile_map: TileMap, state: BossArenaState, depth: int) -> dict[str, object]:
    nodes = 0
    best_score = -inf
    best_action = ("wait", None)
    for action in boss_actions(tile_map, state):
        next_state = apply_boss_action(tile_map, state, action)
        score, child_nodes = _minimax(tile_map, next_state, depth - 1, maximizing=False)
        nodes += child_nodes + 1
        if score > best_score:
            best_score = score
            best_action = action
    return root_result(best_action, nodes, 0)


def _minimax(
    tile_map: TileMap,
    state: BossArenaState,
    depth: int,
    maximizing: bool,
) -> tuple[float, int]:
    if depth <= 0 or is_terminal(tile_map, state):
        return evaluate_state(tile_map, state), 1

    nodes = 1
    if maximizing:
        best = -inf
        for action in boss_actions(tile_map, state):
            next_state = apply_boss_action(tile_map, state, action)
            score, child_nodes = _minimax(tile_map, next_state, depth - 1, maximizing=False)
            nodes += child_nodes
            best = max(best, score)
        return best, nodes

    best = inf
    for action in player_actions(tile_map, state):
        next_state = apply_player_action(state, action)
        score, child_nodes = _minimax(tile_map, next_state, depth - 1, maximizing=True)
        nodes += child_nodes
        best = min(best, score)
    return best, nodes


def _alphabeta_root(tile_map: TileMap, state: BossArenaState, depth: int) -> dict[str, object]:
    nodes = 0
    pruned = 0
    alpha = -inf
    beta = inf
    best_score = -inf
    best_action = ("wait", None)
    actions = boss_actions(tile_map, state)
    for index, action in enumerate(actions):
        next_state = apply_boss_action(tile_map, state, action)
        score, child_nodes, child_pruned = _alphabeta(
            tile_map,
            next_state,
            depth - 1,
            alpha,
            beta,
            maximizing=False,
        )
        nodes += child_nodes + 1
        pruned += child_pruned
        if score > best_score:
            best_score = score
            best_action = action
        alpha = max(alpha, best_score)
        if alpha >= beta:
            pruned += len(actions) - index - 1
            break
    return root_result(best_action, nodes, pruned)


def _alphabeta(
    tile_map: TileMap,
    state: BossArenaState,
    depth: int,
    alpha: float,
    beta: float,
    maximizing: bool,
) -> tuple[float, int, int]:
    if depth <= 0 or is_terminal(tile_map, state):
        return evaluate_state(tile_map, state), 1, 0

    nodes = 1
    pruned = 0
    if maximizing:
        best = -inf
        actions = boss_actions(tile_map, state)
        for index, action in enumerate(actions):
            next_state = apply_boss_action(tile_map, state, action)
            score, child_nodes, child_pruned = _alphabeta(
                tile_map,
                next_state,
                depth - 1,
                alpha,
                beta,
                maximizing=False,
            )
            nodes += child_nodes
            pruned += child_pruned
            best = max(best, score)
            alpha = max(alpha, best)
            if alpha >= beta:
                pruned += len(actions) - index - 1
                break
        return best, nodes, pruned

    best = inf
    actions = player_actions(tile_map, state)
    for index, action in enumerate(actions):
        next_state = apply_player_action(state, action)
        score, child_nodes, child_pruned = _alphabeta(
            tile_map,
            next_state,
            depth - 1,
            alpha,
            beta,
            maximizing=True,
        )
        nodes += child_nodes
        pruned += child_pruned
        best = min(best, score)
        beta = min(beta, best)
        if alpha >= beta:
            pruned += len(actions) - index - 1
            break
    return best, nodes, pruned


def root_result(action: tuple[str, Direction | None], nodes: int, pruned: int) -> dict[str, object]:
    kind, direction = action
    return {
        "direction": direction,
        "should_fire": kind == "shoot",
        "nodes": nodes,
        "pruned": pruned,
    }


def boss_actions(tile_map: TileMap, state: BossArenaState) -> list[tuple[str, Direction | None]]:
    """Return legal boss actions ordered to improve pruning."""
    actions: list[tuple[str, Direction | None]] = []
    shot_direction = boss_shot_direction(tile_map, state)
    if shot_direction is not None:
        actions.append(("shoot", shot_direction))

    for direction, _ in legal_moves(tile_map, state.boss_tile, blocked_tiles={state.player_tile}):
        actions.append(("move", direction))

    actions.append(("wait", None))
    return actions


def player_actions(tile_map: TileMap, state: BossArenaState) -> list[tuple[str, Direction | None]]:
    actions = [("wait", None)]
    actions.extend(
        ("move", direction)
        for direction, _ in legal_moves(tile_map, state.player_tile, blocked_tiles={state.boss_tile})
    )
    return actions


def legal_moves(
    tile_map: TileMap,
    tile: tuple[int, int],
    blocked_tiles: set[tuple[int, int]],
) -> list[tuple[Direction, tuple[int, int]]]:
    mapping = {
        (0, -1): Direction.UP,
        (0, 1): Direction.DOWN,
        (-1, 0): Direction.LEFT,
        (1, 0): Direction.RIGHT,
    }
    moves: list[tuple[Direction, tuple[int, int]]] = []
    for neighbor in neighbor_tiles(tile_map, tile):
        if neighbor in blocked_tiles:
            continue
        dx = neighbor[0] - tile[0]
        dy = neighbor[1] - tile[1]
        moves.append((mapping[(dx, dy)], neighbor))
    return moves


def apply_boss_action(
    tile_map: TileMap,
    state: BossArenaState,
    action: tuple[str, Direction | None],
) -> BossArenaState:
    kind, direction = action
    if kind == "move" and direction is not None:
        return BossArenaState(
            boss_tile=step_tile(state.boss_tile, direction),
            player_tile=state.player_tile,
            eagle_tile=state.eagle_tile,
            boss_hp=state.boss_hp,
            player_lives=state.player_lives,
            eagle_destroyed=state.eagle_destroyed,
        )
    if kind == "shoot" and direction is not None:
        player_lives = state.player_lives
        eagle_destroyed = state.eagle_destroyed
        if direction_between(state.boss_tile, state.eagle_tile) == direction and has_clear_tile_line(
            tile_map, state.boss_tile, state.eagle_tile
        ):
            eagle_destroyed = True
        if direction_between(state.boss_tile, state.player_tile) == direction and has_clear_tile_line(
            tile_map, state.boss_tile, state.player_tile
        ):
            player_lives = max(0, player_lives - 1)
        return BossArenaState(
            boss_tile=state.boss_tile,
            player_tile=state.player_tile,
            eagle_tile=state.eagle_tile,
            boss_hp=state.boss_hp,
            player_lives=player_lives,
            eagle_destroyed=eagle_destroyed,
        )
    return state


def apply_player_action(
    state: BossArenaState,
    action: tuple[str, Direction | None],
) -> BossArenaState:
    kind, direction = action
    if kind == "move" and direction is not None:
        return BossArenaState(
            boss_tile=state.boss_tile,
            player_tile=step_tile(state.player_tile, direction),
            eagle_tile=state.eagle_tile,
            boss_hp=state.boss_hp,
            player_lives=state.player_lives,
            eagle_destroyed=state.eagle_destroyed,
        )
    return state


def boss_shot_direction(tile_map: TileMap, state: BossArenaState) -> Direction | None:
    if has_clear_tile_line(tile_map, state.boss_tile, state.eagle_tile):
        return direction_between(state.boss_tile, state.eagle_tile)
    if has_clear_tile_line(tile_map, state.boss_tile, state.player_tile):
        return direction_between(state.boss_tile, state.player_tile)
    return None


def evaluate_state(tile_map: TileMap, state: BossArenaState) -> float:
    """Score a reduced boss arena state from the boss perspective."""
    if state.eagle_destroyed:
        return 1200.0 + state.boss_hp * 5
    if state.player_lives <= 0:
        return 900.0 + state.boss_hp * 5

    eagle_distance = manhattan_distance(state.boss_tile, state.eagle_tile)
    player_distance = manhattan_distance(state.boss_tile, state.player_tile)
    score = 100.0 - eagle_distance * 12
    score += 40.0 - player_distance * 4
    if has_clear_tile_line(tile_map, state.boss_tile, state.eagle_tile):
        score += 180.0
    if has_clear_tile_line(tile_map, state.boss_tile, state.player_tile):
        score += 90.0
    score += state.boss_hp * 2
    score -= state.player_lives * 25
    return score


def is_terminal(tile_map: TileMap, state: BossArenaState) -> bool:
    return state.player_lives <= 0 or state.eagle_destroyed


def step_tile(tile: tuple[int, int], direction: Direction) -> tuple[int, int]:
    if direction is Direction.UP:
        return (tile[0], tile[1] - 1)
    if direction is Direction.DOWN:
        return (tile[0], tile[1] + 1)
    if direction is Direction.LEFT:
        return (tile[0] - 1, tile[1])
    return (tile[0] + 1, tile[1])
