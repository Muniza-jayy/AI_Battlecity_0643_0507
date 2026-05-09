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
from game.entities.enemy import EnemyTank
from game.entities.tank import Tank
from game.core.state import MatchOutcome
from game.ui.debug_overlay import draw_debug_overlay
from game.ui.theme_assets import tank_sprite, tile_texture
from game.world.tiles import TileMap, TileType


TILE_COLORS: dict[TileType, tuple[int, int, int]] = {
    TileType.EMPTY: (0, 0, 0),
    TileType.BRICK: (168, 86, 50),
    TileType.STEEL: (129, 139, 149),
    TileType.WATER: (43, 104, 160),
    TileType.FOREST: (55, 122, 70),
    TileType.EAGLE: (214, 185, 70),
}

SPAWN_COLOR = (230, 230, 230)
HUD_TEXT_COLOR = (240, 240, 240)


def draw_scene(
    surface: pygame.Surface,
    font: pygame.font.Font,
    tile_map: TileMap,
    player: Tank,
    player_bullet: Bullet | None,
    active_enemies: list[EnemyTank],
    lives: int,
    score: int,
    enemies_remaining: int,
    eagle_destroyed: bool,
    outcome: MatchOutcome,
    paused: bool,
    level_name: str,
    debug_overlay_enabled: bool = False,
    path_visualization_enabled: bool = True,
    map_revision: int = 0,
    enemy_spawn_queue_size: int = 0,
    generated_seed: int | None = None,
) -> None:
    """Draw the full milestone scene for the current frame."""
    surface.fill((0, 0, 0))
    pygame.draw.rect(
        surface,
        HUD_BACKGROUND_COLOR,
        pygame.Rect(MAP_WIDTH, 0, SCREEN_WIDTH - MAP_WIDTH, SCREEN_HEIGHT),
    )
    render_tile_map(surface, tile_map, font)
    draw_player(surface, player)
    draw_enemies(surface, active_enemies, path_visualization_enabled=path_visualization_enabled)
    if player_bullet is not None and player_bullet.active:
        draw_bullet(surface, player_bullet)

    title = font.render("Battle City AI", True, TEXT_COLOR)
    surface.blit(title, (24, 24))

    draw_hud(
        surface,
        font,
        tile_map,
        lives,
        score,
        enemies_remaining,
        eagle_destroyed,
        outcome,
        active_enemies,
        level_name,
    )

    if debug_overlay_enabled:
        draw_debug_overlay(
            surface,
            font,
            level_name=level_name,
            map_revision=map_revision,
            active_enemies=active_enemies,
            enemy_spawn_queue_size=enemy_spawn_queue_size,
            generated_seed=generated_seed,
        )

    if paused:
        pause_label = font.render("Paused", True, TEXT_COLOR)
        surface.blit(pause_label, (MAP_WIDTH + 20, SCREEN_HEIGHT - 60))


def render_tile_map(
    surface: pygame.Surface,
    tile_map: TileMap,
    font: pygame.font.Font,
) -> None:
    """Draw the battlefield with pixel-art terrain textures."""
    for y, row in enumerate(tile_map.tiles):
        for x, tile_type in enumerate(row):
            tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, TILE_COLORS[tile_type], tile_rect)
            surface.blit(tile_texture(tile_type), tile_rect)

    draw_eagle_fortification(surface, tile_map)

def draw_player(surface: pygame.Surface, player: Tank) -> None:
    """Draw the player tank using the active theme sprite."""
    sprite_size = player.size + 10
    sprite = tank_sprite("player", player.facing, sprite_size)
    sprite_rect = sprite.get_rect(center=(round(player.x), round(player.y)))
    shadow = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 55))
    surface.blit(shadow, sprite_rect.move(1, 2))
    surface.blit(sprite, sprite_rect)


def draw_bullet(surface: pygame.Surface, bullet: Bullet) -> None:
    """Draw an active projectile."""
    color = (250, 244, 191) if bullet.owner == "player" else (231, 124, 94)
    pygame.draw.circle(surface, color, (round(bullet.x), round(bullet.y)), bullet.radius)


def draw_enemies(
    surface: pygame.Surface,
    enemies: list[EnemyTank],
    path_visualization_enabled: bool = True,
) -> None:
    """Draw active enemy tanks and any bullets they have fired."""
    for enemy in enemies:
        if path_visualization_enabled:
            draw_enemy_path(surface, enemy)
        body_rect = pygame.Rect(0, 0, enemy.size, enemy.size)
        body_rect.center = (round(enemy.x), round(enemy.y))
        sprite_size = enemy.size + 10
        sprite = tank_sprite(enemy.role, enemy.facing, sprite_size)
        sprite_rect = sprite.get_rect(center=body_rect.center)
        shadow = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 55))
        surface.blit(shadow, sprite_rect.move(1, 2))
        surface.blit(sprite, sprite_rect)

        if enemy.max_hit_points > 1:
            draw_enemy_armor(surface, body_rect, enemy)

        if enemy.bullet is not None and enemy.bullet.active:
            draw_bullet(surface, enemy.bullet)


def draw_enemy_path(surface: pygame.Surface, enemy: EnemyTank) -> None:
    """Overlay the currently planned BFS path for debugging."""
    if len(enemy.debug_path) < 2:
        return

    points = [
        (tile_x * TILE_SIZE + TILE_SIZE // 2, tile_y * TILE_SIZE + TILE_SIZE // 2)
        for tile_x, tile_y in enemy.debug_path
    ]
    pygame.draw.lines(surface, path_color(enemy), False, points, width=2)


def enemy_colors(enemy: EnemyTank) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    if enemy.role == "boss":
        return (176, 74, 72), (74, 18, 18)
    if enemy.role == "fast":
        return (90, 186, 202), (27, 70, 82)
    if enemy.role == "armor":
        return (171, 177, 188), (66, 70, 79)
    return (202, 107, 79), (84, 36, 26)


def path_color(enemy: EnemyTank) -> tuple[int, int, int]:
    if enemy.role == "boss":
        return (255, 154, 146)
    if enemy.role == "fast":
        return (120, 220, 240)
    if enemy.role == "armor":
        return (208, 220, 230)
    return (228, 138, 98)


def draw_enemy_armor(surface: pygame.Surface, body_rect: pygame.Rect, enemy: EnemyTank) -> None:
    pip_width = 7
    gap = 3
    total_width = enemy.max_hit_points * pip_width + (enemy.max_hit_points - 1) * gap
    start_x = body_rect.centerx - total_width // 2
    y = body_rect.top - 8
    for index in range(enemy.max_hit_points):
        color = (242, 214, 88) if index < enemy.hit_points else (87, 91, 99)
        pip_rect = pygame.Rect(start_x + index * (pip_width + gap), y, pip_width, 4)
        pygame.draw.rect(surface, color, pip_rect, border_radius=2)


def draw_hud(
    surface: pygame.Surface,
    font: pygame.font.Font,
    tile_map: TileMap,
    lives: int,
    score: int,
    enemies_remaining: int,
    eagle_destroyed: bool,
    outcome: MatchOutcome,
    active_enemies: list[EnemyTank],
    level_name: str,
) -> None:
    """Draw the current playable-match status in the HUD."""
    hud_x = MAP_WIDTH + 20
    boss = next((enemy for enemy in active_enemies if enemy.role == "boss"), None)
    labels = (
        "Milestone 9",
        "Boss Level Ready",
        f"Level: {level_name}",
        f"Lives: {lives}",
        f"Score: {score}",
        f"Enemies: {enemies_remaining}",
        f"On map: {len(active_enemies)}",
        f"Eagle: {'Destroyed' if eagle_destroyed else 'Safe'}",
        f"Grid: {tile_map.width}x{tile_map.height}",
        "P: pause",
        "Arrows/WASD: move",
        "Space: shoot",
    )
    for index, label in enumerate(labels):
        text_surface = font.render(label, True, HUD_TEXT_COLOR)
        surface.blit(text_surface, (hud_x, 24 + index * 34))

    if boss is not None:
        boss_labels = (
            f"Boss HP: {boss.hit_points}/{boss.max_hit_points}",
            f"Boss phase: {boss.boss_phase}",
            f"Search depth: {boss.boss_search_depth}",
            f"Nodes raw: {boss.nodes_without_pruning}",
            f"Nodes pruned: {boss.nodes_with_pruning}",
            f"Cutoffs: {boss.pruned_nodes}",
            f"Speedup: {boss.speedup_ratio:.2f}x",
        )
        for index, label in enumerate(boss_labels):
            text_surface = font.render(label, True, HUD_TEXT_COLOR)
            surface.blit(text_surface, (hud_x, 430 + index * 28))

    if outcome is MatchOutcome.VICTORY:
        banner = font.render("Victory", True, (150, 235, 155))
        surface.blit(banner, (hud_x, SCREEN_HEIGHT - 94))
    elif outcome is MatchOutcome.DEFEAT:
        banner = font.render("Defeat", True, (235, 120, 120))
        surface.blit(banner, (hud_x, SCREEN_HEIGHT - 94))


def draw_eagle_fortification(surface: pygame.Surface, tile_map: TileMap) -> None:
    """Emphasize the classic brick fort around the eagle when present on the map."""
    eagle_x, eagle_y = tile_map.eagle_position
    fort_tiles = (
        (eagle_x - 2, eagle_y),
        (eagle_x - 1, eagle_y),
        (eagle_x + 1, eagle_y),
        (eagle_x + 2, eagle_y),
        (eagle_x - 1, eagle_y + 1),
        (eagle_x, eagle_y + 1),
        (eagle_x + 1, eagle_y + 1),
    )
    for tile_x, tile_y in fort_tiles:
        if 0 <= tile_x < tile_map.width and 0 <= tile_y < tile_map.height:
            if tile_map.tile_at(tile_x, tile_y) is TileType.BRICK:
                rect = pygame.Rect(tile_x * TILE_SIZE, tile_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                glow = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                glow.fill((255, 128, 64, 18))
                surface.blit(glow, rect)
