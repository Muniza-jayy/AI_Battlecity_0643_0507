"""Early tile-map tests for Milestone 2."""

from config.settings import GRID_HEIGHT, GRID_WIDTH
from game.world.map_loader import load_starter_level
from game.world.tiles import TileType, blocks_bullets, blocks_tanks, is_destructible


def test_starter_level_matches_configured_dimensions() -> None:
    tile_map = load_starter_level()

    assert tile_map.width == GRID_WIDTH
    assert tile_map.height == GRID_HEIGHT
    assert len(tile_map.tiles) == GRID_HEIGHT
    assert all(len(row) == GRID_WIDTH for row in tile_map.tiles)


def test_tile_rule_flags_match_expected_behavior() -> None:
    assert blocks_tanks(TileType.BRICK) is True
    assert blocks_bullets(TileType.BRICK) is True
    assert blocks_bullets(TileType.STEEL) is True
    assert is_destructible(TileType.BRICK) is True
    assert blocks_tanks(TileType.FOREST) is False


def test_eagle_position_contains_eagle_tile() -> None:
    tile_map = load_starter_level()
    eagle_x, eagle_y = tile_map.eagle_position

    assert tile_map.tile_at(eagle_x, eagle_y) is TileType.EAGLE
