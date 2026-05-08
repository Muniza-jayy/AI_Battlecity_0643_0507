"""Player tank creation and movement."""

from __future__ import annotations

from config.balance import ALIGNMENT_THRESHOLD, PLAYER_SPEED, TANK_SIZE
from config.settings import TILE_SIZE
from game.entities.tank import Direction, Tank, direction_vector
from game.world.alignment import align_toward_lane_center, is_near_lane_center
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


def move_player(player: Tank, desired_direction: Direction | None, tile_map: TileMap) -> None:
    """Move the player tank with solid collision and lane alignment."""
    if desired_direction is None:
        return

    player.facing = desired_direction
    dx, dy = direction_vector(desired_direction)

    next_x = player.x
    next_y = player.y

    if dx != 0:
        if not is_near_lane_center(player.y, TILE_SIZE, ALIGNMENT_THRESHOLD):
            return
        next_y = align_toward_lane_center(player.y, TILE_SIZE, player.speed, ALIGNMENT_THRESHOLD)
        next_x += dx * player.speed
    else:
        if not is_near_lane_center(player.x, TILE_SIZE, ALIGNMENT_THRESHOLD):
            return
        next_x = align_toward_lane_center(player.x, TILE_SIZE, player.speed, ALIGNMENT_THRESHOLD)
        next_y += dy * player.speed

    if tank_can_occupy(next_x, next_y, player.size, tile_map):
        player.x = next_x
        player.y = next_y
        return

    # If forward motion is blocked, still allow a small legal alignment nudge.
    if dx != 0 and next_y != player.y and tank_can_occupy(player.x, next_y, player.size, tile_map):
        player.y = next_y
    elif dy != 0 and next_x != player.x and tank_can_occupy(next_x, player.y, player.size, tile_map):
        player.x = next_x
