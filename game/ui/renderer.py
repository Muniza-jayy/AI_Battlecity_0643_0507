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
from game.entities.bullet import Bullet
from game.entities.tank import Direction, Tank
from game.core.state import MatchOutcome
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
    player: Tank,
    player_bullet: Bullet | None,
    lives: int,
    score: int,
    enemies_remaining: int,
    eagle_destroyed: bool,
    outcome: MatchOutcome,
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
    draw_player(surface, player)
    if player_bullet is not None and player_bullet.active:
        draw_bullet(surface, player_bullet)

    title = font.render("Battle City AI", True, TEXT_COLOR)
    surface.blit(title, (24, 24))

    draw_hud(surface, font, tile_map, lives, score, enemies_remaining, eagle_destroyed, outcome)

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

def draw_player(surface: pygame.Surface, player: Tank) -> None:
    """Draw the player tank body and facing marker."""
    body_rect = pygame.Rect(0, 0, player.size, player.size)
    body_rect.center = (round(player.x), round(player.y))
    pygame.draw.rect(surface, (235, 214, 92), body_rect, border_radius=6)
    pygame.draw.rect(surface, (80, 64, 24), body_rect, width=2, border_radius=6)

    center = body_rect.center
    half = player.size // 2
    barrel_end = {
        Direction.UP: (center[0], center[1] - half - 6),
        Direction.DOWN: (center[0], center[1] + half + 6),
        Direction.LEFT: (center[0] - half - 6, center[1]),
        Direction.RIGHT: (center[0] + half + 6, center[1]),
    }[player.facing]
    pygame.draw.line(surface, (80, 64, 24), center, barrel_end, width=4)


def draw_bullet(surface: pygame.Surface, bullet: Bullet) -> None:
    """Draw an active projectile."""
    pygame.draw.circle(surface, (250, 244, 191), (round(bullet.x), round(bullet.y)), bullet.radius)


def draw_hud(
    surface: pygame.Surface,
    font: pygame.font.Font,
    tile_map: TileMap,
    lives: int,
    score: int,
    enemies_remaining: int,
    eagle_destroyed: bool,
    outcome: MatchOutcome,
) -> None:
    """Draw the current playable-match status in the HUD."""
    hud_x = MAP_WIDTH + 20
    labels = (
        "Milestone 6",
        "Match Rules Ready",
        f"Lives: {lives}",
        f"Score: {score}",
        f"Enemies: {enemies_remaining}",
        f"Eagle: {'Destroyed' if eagle_destroyed else 'Safe'}",
        f"Grid: {tile_map.width}x{tile_map.height}",
        "P: pause",
        "Arrows/WASD: move",
        "Space: shoot",
    )
    for index, label in enumerate(labels):
        text_surface = font.render(label, True, HUD_TEXT_COLOR)
        surface.blit(text_surface, (hud_x, 24 + index * 34))

    if outcome is MatchOutcome.VICTORY:
        banner = font.render("Victory", True, (150, 235, 155))
        surface.blit(banner, (hud_x, SCREEN_HEIGHT - 94))
    elif outcome is MatchOutcome.DEFEAT:
        banner = font.render("Defeat", True, (235, 120, 120))
        surface.blit(banner, (hud_x, SCREEN_HEIGHT - 94))


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
