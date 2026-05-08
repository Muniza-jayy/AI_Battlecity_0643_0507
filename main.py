"""Bootstrap entry point for the Battle City AI project."""

from __future__ import annotations

from typing import Optional

import pygame  # type: ignore[import]

from config.settings import SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE
from game.core.loop import create_display, run_application_loop
from game.core.state import AppState
from game.modes.level_flow import create_starter_game_state
from game.ui.screens import UIFontPack


def main(max_frames: Optional[int] = None) -> int:
    """Run the initial Pygame application."""
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)

    window = create_display(max_frames)
    scene = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fonts = build_fonts()
    app_state = AppState(game_state=create_starter_game_state())

    try:
        return run_application_loop(window, scene, fonts, app_state, max_frames=max_frames)
    finally:
        pygame.quit()


def build_fonts() -> UIFontPack:
    """Create the font pack used by the screen system."""
    title = pygame.font.SysFont("Avenir Next,Helvetica Neue,Arial", 72, bold=True)
    subtitle = pygame.font.SysFont("Menlo,Monaco,Courier New", 26, bold=False)
    body = pygame.font.SysFont("Avenir Next,Helvetica Neue,Arial", 32)
    button = pygame.font.SysFont("Avenir Next,Helvetica Neue,Arial", 28, bold=True)
    small = pygame.font.SysFont("Menlo,Monaco,Courier New", 18)
    return UIFontPack(title=title, subtitle=subtitle, body=body, button=button, small=small)


if __name__ == "__main__":
    raise SystemExit(main())
