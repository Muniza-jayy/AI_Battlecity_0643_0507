"""Projectile behavior tests for Milestone 5."""

from config.settings import GRID_HEIGHT, GRID_WIDTH
from game.entities.bullet import spawn_bullet_from_tank
from game.entities.player import spawn_player
from game.entities.tank import Direction
from game.world.map_loader import build_tile_map
from game.world.projectiles import BulletHit, advance_bullet
from game.world.tiles import TileType


def empty_layout() -> list[str]:
    return ["." * GRID_WIDTH for _ in range(GRID_HEIGHT)]


def replace_char(source: str, index: int, value: str) -> str:
    return source[:index] + value + source[index + 1 :]


def test_bullet_spawns_from_player_facing_direction() -> None:
    layout = empty_layout()
    layout[5] = replace_char(layout[5], 5, "E")
    tile_map = build_tile_map(layout, (2, 2), ((0, 0),), (5, 5))
    player = spawn_player((2, 2))

    bullet = spawn_bullet_from_tank(player, owner="player")

    assert bullet.y < player.y
    assert bullet.dx == 0
    assert bullet.dy == -1


def test_bullet_destroys_brick_and_stops() -> None:
    layout = empty_layout()
    layout[2] = replace_char(layout[2], 3, "B")
    layout[5] = replace_char(layout[5], 5, "E")
    tile_map = build_tile_map(layout, (2, 2), ((0, 0),), (5, 5))
    player = spawn_player((2, 2))
    player.facing = Direction.RIGHT
    bullet = spawn_bullet_from_tank(player, owner="player")

    hit = BulletHit.NONE
    for _ in range(10):
        impact = advance_bullet(bullet, tile_map)
        hit = impact.hit
        if hit is not BulletHit.NONE:
            break

    assert bullet.active is False
    assert hit is BulletHit.BRICK
    assert tile_map.tile_at(3, 2) is TileType.EMPTY
    assert tile_map.revision == 1


def test_bullet_stops_on_steel_without_destroying_it() -> None:
    layout = empty_layout()
    layout[2] = replace_char(layout[2], 3, "S")
    layout[5] = replace_char(layout[5], 5, "E")
    tile_map = build_tile_map(layout, (2, 2), ((0, 0),), (5, 5))
    player = spawn_player((2, 2))
    player.facing = Direction.RIGHT
    bullet = spawn_bullet_from_tank(player, owner="player")

    hit = BulletHit.NONE
    for _ in range(10):
        impact = advance_bullet(bullet, tile_map)
        hit = impact.hit
        if hit is not BulletHit.NONE:
            break

    assert bullet.active is False
    assert hit is BulletHit.STEEL
    assert tile_map.tile_at(3, 2) is TileType.STEEL


def test_bullet_leaving_map_becomes_inactive() -> None:
    layout = empty_layout()
    layout[5] = replace_char(layout[5], 5, "E")
    tile_map = build_tile_map(layout, (0, 0), ((0, 0),), (5, 5))
    player = spawn_player((0, 0))
    bullet = spawn_bullet_from_tank(player, owner="player")

    for _ in range(10):
        advance_bullet(bullet, tile_map)
        if not bullet.active:
            break

    assert bullet.active is False


def test_bullet_hitting_eagle_reports_eagle_hit() -> None:
    layout = empty_layout()
    layout[2] = replace_char(layout[2], 3, "E")
    tile_map = build_tile_map(layout, (2, 2), ((0, 0),), (3, 2))
    player = spawn_player((2, 2))
    player.facing = Direction.RIGHT
    bullet = spawn_bullet_from_tank(player, owner="player")

    hit = BulletHit.NONE
    for _ in range(10):
        impact = advance_bullet(bullet, tile_map)
        hit = impact.hit
        if hit is not BulletHit.NONE:
            break

    assert bullet.active is False
    assert hit is BulletHit.EAGLE
