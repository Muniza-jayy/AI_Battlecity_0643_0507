"""Milestone 1 bootstrap for the Battle City AI project."""

from __future__ import annotations

import os
from typing import Optional

import pygame  # type: ignore[import]

from config.settings import (
    BACKGROUND_COLOR,
    FPS,
    HUD_BACKGROUND_COLOR,
    MAP_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TEXT_COLOR,
    WINDOW_TITLE,
)
from game.ui.renderer import render_tile_map
from game.world.map_loader import load_starter_level


def draw_placeholder(screen: pygame.Surface, font: pygame.font.Font) -> None:
    """Draw a minimal placeholder layout for the initial project bootstrap."""
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(
        screen,
        HUD_BACKGROUND_COLOR,
        pygame.Rect(MAP_WIDTH, 0, SCREEN_WIDTH - MAP_WIDTH, SCREEN_HEIGHT),
    )

    label = font.render("Battle City AI", True, TEXT_COLOR)
    hint = font.render("Milestone 1 bootstrap", True, TEXT_COLOR)
    screen.blit(label, (24, 24))
    screen.blit(hint, (24, 56))


def compute_letterbox(
    content_width: int,
    content_height: int,
    window_width: int,
    window_height: int,
) -> pygame.Rect:
    """Fit the fixed game surface into the window without stretching."""
    if window_width <= 0 or window_height <= 0:
        return pygame.Rect(0, 0, 1, 1)

    scale = min(window_width / content_width, window_height / content_height)
    scaled_width = max(1, int(content_width * scale))
    scaled_height = max(1, int(content_height * scale))
    offset_x = (window_width - scaled_width) // 2
    offset_y = (window_height - scaled_height) // 2
    return pygame.Rect(offset_x, offset_y, scaled_width, scaled_height)


def create_display(max_frames: Optional[int]) -> pygame.Surface:
    """Create the main window, falling back to dummy video for smoke checks."""
    flags = pygame.RESIZABLE
    try:
        return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    except pygame.error:
        if max_frames is None or os.environ.get("SDL_VIDEODRIVER"):
            raise

    pygame.quit()
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)


def main(max_frames: Optional[int] = None) -> int:
    """Run the initial Pygame loop.

    `max_frames` is used for automated smoke checks in headless mode.
    """
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)

    window = create_display(max_frames)
    scene = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    tile_map = load_starter_level()

    frame_count = 0
    running = True

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    window = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            draw_placeholder(scene, font)
            render_tile_map(scene, tile_map, font)

            window_width, window_height = window.get_size()
            viewport = compute_letterbox(
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
                window_width,
                window_height,
            )

            window.fill(BACKGROUND_COLOR)
            scaled_scene = pygame.transform.smoothscale(scene, viewport.size)
            window.blit(scaled_scene, viewport.topleft)
            pygame.display.flip()

            clock.tick(FPS)
            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                running = False
    finally:
        pygame.quit()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
