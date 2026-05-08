"""Optional debug overlay for AI labels, timers, and simulation info."""

from __future__ import annotations

import pygame  # type: ignore[import]

from game.entities.enemy import EnemyTank


OVERLAY_BG = (8, 10, 14, 190)
OVERLAY_TEXT = (237, 242, 246)


def draw_debug_overlay(
    surface: pygame.Surface,
    font: pygame.font.Font,
    *,
    level_name: str,
    map_revision: int,
    active_enemies: list[EnemyTank],
    enemy_spawn_queue_size: int,
    generated_seed: int | None,
) -> None:
    """Render optional debug information over the map area."""
    panel = pygame.Surface((330, 146), pygame.SRCALPHA)
    panel.fill(OVERLAY_BG)
    surface.blit(panel, (12, 58))

    labels = (
        f"Debug overlay: ON",
        f"Mode: {level_name}",
        f"Map revision: {map_revision}",
        f"Enemies active: {len(active_enemies)}",
        f"Spawn queue: {enemy_spawn_queue_size}",
        f"Seed: {generated_seed if generated_seed is not None else 'fixed'}",
        "F1: overlay  F5: CSP map",
    )
    for index, label in enumerate(labels):
        text = font.render(label, True, OVERLAY_TEXT)
        surface.blit(text, (24, 68 + index * 18))

    for enemy in active_enemies:
        draw_enemy_debug_label(surface, font, enemy)


def draw_enemy_debug_label(surface: pygame.Surface, font: pygame.font.Font, enemy: EnemyTank) -> None:
    label = f"{enemy.role} d:{enemy.frames_until_decision}"
    if enemy.role == "boss":
        label += f" p:{enemy.boss_phase}"
    text = font.render(label, True, OVERLAY_TEXT)
    rect = text.get_rect(midbottom=(round(enemy.x), round(enemy.y - enemy.size / 2 - 6)))
    bg = pygame.Surface((rect.width + 8, rect.height + 4), pygame.SRCALPHA)
    bg.fill((10, 12, 18, 180))
    surface.blit(bg, (rect.x - 4, rect.y - 2))
    surface.blit(text, rect)
