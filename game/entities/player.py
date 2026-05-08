"""Player tank creation and movement."""

from __future__ import annotations

from config.balance import ALIGNMENT_THRESHOLD, PLAYER_SPEED, TANK_SIZE
from config.settings import TILE_SIZE
from game.entities.tank import Direction, Tank, direction_vector
from game.world.alignment import (
    align_toward_lane_center,
    is_near_lane_center,
    step_toward_lane_center,
)
from game.world.collision import tank_can_occupy
from game.world.tiles import TileMap


def spawn_player(spawn_tile: tuple[int, int]) -> Tank:
    """Create the player tank centered on its spawn tile."""
    tile_x, tile_y = spawn_tile
    return Tank(
        x=tile_x * TILE_SIZE + TILE_SIZE / 2,
        y=tile_y * TILE_SIZE + TILE_SIZE / 2,
        size=TANK_SIZE,
        speed=PLAYER_SPEED,
        facing=Direction.UP,
    )


def move_tank(
    tank: Tank,
    desired_direction: Direction | None,
    tile_map: TileMap,
    blocking_tanks: tuple[Tank, ...] = (),
) -> None:
    """Move a tank with solid collision and lane alignment."""
    if desired_direction is None:
        return

    tank.facing = desired_direction
    dx, dy = direction_vector(desired_direction)

    next_x = tank.x
    next_y = tank.y

    if dx != 0:
        if not is_near_lane_center(tank.y, TILE_SIZE, ALIGNMENT_THRESHOLD):
            aligned_y = step_toward_lane_center(tank.y, TILE_SIZE, tank.speed)
            if aligned_y != tank.y and tank_can_occupy(
                tank.x,
                aligned_y,
                tank.size,
                tile_map,
                blocking_tanks=blocking_tanks,
            ):
                tank.y = aligned_y
            return
        next_y = align_toward_lane_center(tank.y, TILE_SIZE, tank.speed, ALIGNMENT_THRESHOLD)
        next_x += dx * tank.speed
    else:
        if not is_near_lane_center(tank.x, TILE_SIZE, ALIGNMENT_THRESHOLD):
            aligned_x = step_toward_lane_center(tank.x, TILE_SIZE, tank.speed)
            if aligned_x != tank.x and tank_can_occupy(
                aligned_x,
                tank.y,
                tank.size,
                tile_map,
                blocking_tanks=blocking_tanks,
            ):
                tank.x = aligned_x
            return
        next_x = align_toward_lane_center(tank.x, TILE_SIZE, tank.speed, ALIGNMENT_THRESHOLD)
        next_y += dy * tank.speed

    if tank_can_occupy(next_x, next_y, tank.size, tile_map, blocking_tanks=blocking_tanks):
        tank.x = next_x
        tank.y = next_y
        return

    # If forward motion is blocked, still allow a small legal alignment nudge.
    if dx != 0 and next_y != tank.y and tank_can_occupy(
        tank.x,
        next_y,
        tank.size,
        tile_map,
        blocking_tanks=blocking_tanks,
    ):
        tank.y = next_y
    elif dy != 0 and next_x != tank.x and tank_can_occupy(
        next_x,
        tank.y,
        tank.size,
        tile_map,
        blocking_tanks=blocking_tanks,
    ):
        tank.x = next_x


def move_player(
    player: Tank,
    desired_direction: Direction | None,
    tile_map: TileMap,
    blocking_tanks: tuple[Tank, ...] = (),
) -> None:
    """Move the player tank with solid collision and lane alignment."""
    move_tank(player, desired_direction, tile_map, blocking_tanks=blocking_tanks)
