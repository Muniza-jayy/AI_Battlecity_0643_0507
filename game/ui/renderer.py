"""Rendering helpers for the initial tile-map milestone."""

from __future__ import annotations

import pygame  # type: ignore[import]

from config.settings import (
    BACKGROUND_COLOR,
    HUD_BACKGROUND_COLOR,
    HUD_WIDTH,
    MAP_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TEXT_COLOR,
    TILE_SIZE,
)
from game.world.tiles import TileMap, TileType


TILE_COLORS: dict[TileType, tuple[int, int, int]] = {
    TileType.EMPTY: (44, 51, 60),
    TileType.BRICK: (168, 86, 50),
    TileType.STEEL: (129, 139, 149),
    TileType.WATER: (43, 104, 160),
    TileType.FOREST: (55, 122, 70),
    TileType.EAGLE: (214, 185, 70),
}

SPAWN_COLOR = (230, 230, 230)
GRID_LINE_COLOR = (26, 30, 38)
HUD_TEXT_COLOR = (240, 240, 240)


def draw_scene(
    surface: pygame.Surface,
    font: pygame.font.Font,
    tile_map: TileMap,
    paused: bool,
) -> None:
    """Draw the full milestone scene for the current frame."""
    surface.fill(BACKGROUND_COLOR)
    pygame.draw.rect(
        surface,
        HUD_BACKGROUND_COLOR,
        pygame.Rect(MAP_WIDTH, 0, SCREEN_WIDTH - MAP_WIDTH, SCREEN_HEIGHT),
    )
    render_tile_map(surface, tile_map, font)

    title = font.render("Battle City AI", True, TEXT_COLOR)
    surface.blit(title, (24, 24))

    if paused:
        pause_label = font.render("Paused", True, TEXT_COLOR)
        surface.blit(pause_label, (MAP_WIDTH + 20, SCREEN_HEIGHT - 60))


def render_tile_map(
    surface: pygame.Surface,
    tile_map: TileMap,
    font: pygame.font.Font,
) -> None:
    """Draw the starter level using flat colors and simple markers."""
    for y, row in enumerate(tile_map.tiles):
        for x, tile_type in enumerate(row):
            tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, TILE_COLORS[tile_type], tile_rect)
            pygame.draw.rect(surface, GRID_LINE_COLOR, tile_rect, width=1)

    _draw_spawn_marker(surface, tile_map.player_spawn, "P")
    for enemy_spawn in tile_map.enemy_spawns:
        _draw_spawn_marker(surface, enemy_spawn, "X")

    hud_x = MAP_WIDTH + 20
    labels = (
        "Milestone 3",
        "Core Loop Ready",
        f"Grid: {tile_map.width}x{tile_map.height}",
        f"Tile: {TILE_SIZE}px",
        f"HUD: {HUD_WIDTH}px",
        "P: pause",
    )
    for index, label in enumerate(labels):
        text_surface = font.render(label, True, HUD_TEXT_COLOR)
        surface.blit(text_surface, (hud_x, 24 + index * 34))


def _draw_spawn_marker(surface: pygame.Surface, position: tuple[int, int], label: str) -> None:
    center_x = position[0] * TILE_SIZE + TILE_SIZE // 2
    center_y = position[1] * TILE_SIZE + TILE_SIZE // 2
    radius = max(6, TILE_SIZE // 4)
    pygame.draw.circle(surface, SPAWN_COLOR, (center_x, center_y), radius, width=2)

    if label == "P":
        pygame.draw.line(
            surface,
            SPAWN_COLOR,
            (center_x, center_y - radius + 2),
            (center_x, center_y + radius - 2),
            width=2,
        )
    else:
        pygame.draw.line(
            surface,
            SPAWN_COLOR,
            (center_x - radius + 2, center_y - radius + 2),
            (center_x + radius - 2, center_y + radius - 2),
            width=2,
        )
        pygame.draw.line(
            surface,
            SPAWN_COLOR,
            (center_x + radius - 2, center_y - radius + 2),
            (center_x - radius + 2, center_y + radius - 2),
            width=2,
        )
