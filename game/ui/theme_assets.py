"""Shared Battle City-style theme assets with file loading and procedural fallbacks."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pygame  # type: ignore[import]

from config.settings import TILE_SIZE
from game.entities.tank import Direction
from game.world.tiles import TileType


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_ROOT = PROJECT_ROOT / "assets"
TILES_DIR = ASSETS_ROOT / "tiles"
TANKS_DIR = ASSETS_ROOT / "tanks"
UI_DIR = ASSETS_ROOT / "ui"

BLACK = (0, 0, 0)
ROAD_DARK = (2, 2, 4)
ROAD_MID = (10, 10, 14)
ROAD_DUST = (30, 22, 18)

TILE_ASSET_PATHS: dict[TileType, Path] = {
    TileType.EMPTY: TILES_DIR / "road.png",
    TileType.BRICK: TILES_DIR / "brick.png",
    TileType.STEEL: TILES_DIR / "steel.png",
    TileType.WATER: TILES_DIR / "water.png",
    TileType.FOREST: TILES_DIR / "forest.png",
    TileType.EAGLE: TILES_DIR / "eagle.png",
}

TANK_ASSET_PATHS: dict[str, Path] = {
    "player": TANKS_DIR / "player.png",
    "basic": TANKS_DIR / "basic.png",
    "fast": TANKS_DIR / "fast.png",
    "armor": TANKS_DIR / "armor.png",
    "boss": TANKS_DIR / "boss.png",
}

WELCOME_HERO_PATH = UI_DIR / "welcome_hero.png"


def _convert_surface(surface: pygame.Surface, *, alpha: bool) -> pygame.Surface:
    if not pygame.display.get_init():
        return surface
    try:
        return surface.convert_alpha() if alpha else surface.convert()
    except pygame.error:
        return surface


def _new_pixel_surface(size: int) -> pygame.Surface:
    return pygame.Surface((size, size), pygame.SRCALPHA)


def _scale_pixel_art(surface: pygame.Surface, width: int, height: int) -> pygame.Surface:
    return pygame.transform.scale(surface, (width, height))


def _rotate_for_facing(surface: pygame.Surface, facing: Direction) -> pygame.Surface:
    angle = {
        Direction.UP: 0,
        Direction.RIGHT: -90,
        Direction.DOWN: 180,
        Direction.LEFT: 90,
    }[facing]
    return pygame.transform.rotate(surface, angle) if angle else surface


@lru_cache(maxsize=None)
def _load_image(path: str, alpha: bool) -> pygame.Surface | None:
    file_path = Path(path)
    if not file_path.exists():
        return None
    loaded = pygame.image.load(str(file_path))
    return _convert_surface(loaded, alpha=alpha)


def _road_surface(size: int = 16) -> pygame.Surface:
    surface = _new_pixel_surface(size)
    surface.fill(ROAD_DARK)
    for x, y in ((2, 3), (5, 4), (9, 2), (12, 5), (4, 10), (7, 8), (11, 12), (14, 9)):
        pygame.draw.rect(surface, ROAD_MID, pygame.Rect(x, y, 2, 2))
    for x, y in ((1, 13), (6, 14), (10, 7), (13, 2), (8, 12), (3, 7)):
        pygame.draw.rect(surface, ROAD_DUST, pygame.Rect(x, y, 1, 1))
    pygame.draw.line(surface, (18, 18, 22), (0, 0), (size - 1, 0))
    return surface


def _brick_surface(size: int = 16) -> pygame.Surface:
    surface = _new_pixel_surface(size)
    surface.fill((40, 14, 10))
    brick = (198, 98, 36)
    highlight = (246, 164, 76)
    shadow = (112, 44, 18)
    rows = ((1, 1, 0), (1, 6, 3), (1, 11, 0))
    for x_start, y, offset in rows:
        for x in range(x_start + offset, size - 1, 7):
            pygame.draw.rect(surface, brick, pygame.Rect(x, y, 6, 4))
            pygame.draw.line(surface, highlight, (x, y), (x + 5, y))
            pygame.draw.line(surface, shadow, (x, y + 3), (x + 5, y + 3))
            pygame.draw.line(surface, (74, 28, 14), (x, y), (x, y + 3))
    return surface


def _steel_surface(size: int = 16) -> pygame.Surface:
    surface = _new_pixel_surface(size)
    surface.fill((172, 176, 184))
    for offset in range(-size, size * 2, 4):
        pygame.draw.line(surface, (234, 238, 242), (offset, 0), (offset - size, size), 1)
        pygame.draw.line(surface, (122, 126, 134), (offset + 1, 0), (offset - size + 1, size), 1)
    pygame.draw.rect(surface, (206, 210, 216), pygame.Rect(1, 1, size - 2, size - 2), 1)
    for point in ((3, 3), (12, 3), (3, 12), (12, 12), (7, 7), (7, 3), (7, 12)):
        pygame.draw.circle(surface, (88, 92, 98), point, 1)
    return surface


def _forest_surface(size: int = 16) -> pygame.Surface:
    surface = _new_pixel_surface(size)
    surface.fill((0, 0, 0, 0))
    trunk = (86, 48, 18)
    canopy_dark = (24, 108, 28)
    canopy_mid = (38, 164, 40)
    canopy_light = (78, 214, 72)
    for cx, cy in ((4, 4), (11, 4), (4, 11), (11, 11)):
        pygame.draw.rect(surface, trunk, pygame.Rect(cx - 1, cy + 2, 2, 3))
        pygame.draw.circle(surface, canopy_dark, (cx, cy), 4)
        pygame.draw.circle(surface, canopy_mid, (cx - 1, cy - 1), 3)
        pygame.draw.circle(surface, canopy_light, (cx + 1, cy - 2), 2)
    return surface


def _water_surface(size: int = 16) -> pygame.Surface:
    surface = _new_pixel_surface(size)
    surface.fill((22, 92, 168))
    for y in range(2, size, 4):
        pygame.draw.arc(surface, (120, 204, 242), pygame.Rect(-2, y, 8, 4), 0.3, 2.8, 1)
        pygame.draw.arc(surface, (44, 130, 210), pygame.Rect(6, y, 8, 4), 0.3, 2.8, 1)
        pygame.draw.arc(surface, (140, 224, 250), pygame.Rect(12, y, 8, 4), 0.3, 2.8, 1)
    pygame.draw.line(surface, (186, 238, 255), (0, 1), (size - 1, 1))
    return surface


def _eagle_surface(size: int = 16) -> pygame.Surface:
    surface = _new_pixel_surface(size)
    surface.fill((8, 6, 4))
    gold = (226, 186, 62)
    shadow = (148, 104, 28)
    outline = (72, 36, 10)
    for x, y in (
        (7, 2), (6, 3), (8, 3), (5, 4), (9, 4), (4, 5), (10, 5), (5, 6), (9, 6),
        (6, 7), (8, 7), (7, 8), (5, 9), (9, 9), (4, 10), (10, 10), (3, 11), (11, 11),
    ):
        surface.set_at((x, y), gold)
    for x, y in ((7, 5), (6, 10), (8, 10), (7, 12)):
        surface.set_at((x, y), shadow)
    pygame.draw.rect(surface, (106, 54, 18), pygame.Rect(1, 1, 14, 14), 1)
    pygame.draw.rect(surface, outline, pygame.Rect(2, 2, 12, 12), 1)
    return surface


def _tank_body_surface(role: str, size: int = 16) -> pygame.Surface:
    palettes = {
        "player": ((214, 176, 72), (248, 218, 104), (102, 70, 24)),
        "basic": ((170, 66, 54), (220, 112, 88), (76, 20, 16)),
        "fast": ((84, 176, 198), (138, 226, 236), (22, 74, 90)),
        "armor": ((116, 156, 88), (174, 202, 132), (46, 70, 34)),
        "boss": ((144, 70, 70), (212, 122, 114), (54, 16, 16)),
    }
    body, highlight, shadow = palettes.get(role, palettes["basic"])
    surface = _new_pixel_surface(size)
    surface.fill((0, 0, 0, 0))

    track_left = pygame.Rect(1, 2, 4, 12)
    track_right = pygame.Rect(11, 2, 4, 12)
    hull = pygame.Rect(4, 4, 8, 9)
    turret = pygame.Rect(5, 5, 6, 5)
    barrel = pygame.Rect(7, 0, 2, 6)

    if role == "fast":
        turret = pygame.Rect(5, 5, 6, 4)
        barrel = pygame.Rect(7, -1, 2, 7)
    elif role == "armor":
        hull = pygame.Rect(3, 4, 10, 10)
        turret = pygame.Rect(5, 5, 6, 6)
    elif role == "boss":
        track_left = pygame.Rect(0, 2, 4, 12)
        track_right = pygame.Rect(12, 2, 4, 12)
        hull = pygame.Rect(2, 4, 12, 10)
        turret = pygame.Rect(4, 5, 8, 6)
        barrel = pygame.Rect(7, -2, 2, 8)

    pygame.draw.rect(surface, shadow, track_left)
    pygame.draw.rect(surface, shadow, track_right)
    for y in range(3, 14, 3):
        pygame.draw.line(surface, (26, 26, 28), (track_left.x + 1, y), (track_left.right - 2, y), 1)
        pygame.draw.line(surface, (26, 26, 28), (track_right.x + 1, y), (track_right.right - 2, y), 1)

    pygame.draw.rect(surface, body, hull)
    pygame.draw.rect(surface, highlight, pygame.Rect(hull.x + 1, hull.y + 1, hull.width - 2, 2))
    pygame.draw.rect(surface, shadow, hull, 1)
    pygame.draw.rect(surface, body, turret)
    pygame.draw.rect(surface, highlight, pygame.Rect(turret.x + 1, turret.y + 1, turret.width - 2, 1))
    pygame.draw.rect(surface, shadow, turret, 1)
    pygame.draw.rect(surface, body, barrel)
    pygame.draw.rect(surface, highlight, pygame.Rect(barrel.x, barrel.y, 1, max(1, barrel.height - 1)))
    pygame.draw.rect(surface, shadow, barrel, 1)
    return surface


def _procedural_tile_surface(tile_type: TileType) -> pygame.Surface:
    if tile_type is TileType.BRICK:
        return _brick_surface()
    if tile_type is TileType.STEEL:
        return _steel_surface()
    if tile_type is TileType.FOREST:
        return _forest_surface()
    if tile_type is TileType.WATER:
        return _water_surface()
    if tile_type is TileType.EAGLE:
        return _eagle_surface()
    return _road_surface()


def _procedural_tank_surface(role: str) -> pygame.Surface:
    return _tank_body_surface(role)


@lru_cache(maxsize=None)
def tile_texture(tile_type: TileType, size: int = TILE_SIZE) -> pygame.Surface:
    """Return a scaled tile texture from assets or a procedural fallback."""
    loaded = _load_image(str(TILE_ASSET_PATHS[tile_type]), alpha=True)
    base = loaded if loaded is not None else _procedural_tile_surface(tile_type)
    return _scale_pixel_art(base, size, size)


@lru_cache(maxsize=None)
def tank_sprite(role: str, facing: Direction, size: int) -> pygame.Surface:
    """Return a scaled tank sprite from assets or a procedural fallback."""
    loaded = _load_image(str(TANK_ASSET_PATHS.get(role, TANK_ASSET_PATHS["basic"])), alpha=True)
    base = loaded if loaded is not None else _procedural_tank_surface(role)
    scaled = _scale_pixel_art(base, size, size)
    return _rotate_for_facing(scaled, facing)


def _procedural_welcome_hero(width: int, height: int) -> pygame.Surface:
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill((4, 4, 6))
    ground = pygame.Rect(0, height - height // 4, width, height // 4)
    pygame.draw.rect(surface, (18, 12, 10), ground)
    for x in range(0, width, 18):
        pygame.draw.rect(surface, (72, 36, 24), pygame.Rect(x, ground.y + 10 + (x // 18) % 6, 10, 5))

    brick = _scale_pixel_art(_brick_surface(), 48, 48)
    steel = _scale_pixel_art(_steel_surface(), 48, 48)
    forest = _scale_pixel_art(_forest_surface(), 48, 48)
    water = _scale_pixel_art(_water_surface(), 48, 48)
    player = _scale_pixel_art(_procedural_tank_surface("player"), 96, 96)
    enemy = _rotate_for_facing(_scale_pixel_art(_procedural_tank_surface("basic"), 96, 96), Direction.LEFT)

    for x in range(18, min(width - 48, 150), 50):
        surface.blit(brick, (x, ground.y - 20))
    surface.blit(steel, (width - 86, 18))
    surface.blit(forest, (24, 30))
    surface.blit(forest, (width - 84, height - 138))
    surface.blit(water, (width - 116, height - 102))
    surface.blit(player, (36, ground.y - 60))
    surface.blit(enemy, (width - 140, ground.y - 60))
    return surface


@lru_cache(maxsize=8)
def welcome_art_scaled(width: int, height: int) -> pygame.Surface:
    """Return a welcome hero image from assets or a procedural fallback scene."""
    loaded = _load_image(str(WELCOME_HERO_PATH), alpha=True)
    base = loaded if loaded is not None else _procedural_welcome_hero(max(200, width), max(120, height))
    return _scale_pixel_art(base, width, height)
