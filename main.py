"""Bootstrap entry point for the Battle City AI project."""

from __future__ import annotations

from typing import Optional

import pygame  # type: ignore[import]

from config.settings import SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE
from game.core.loop import create_display, run_fixed_step
from game.modes.level_flow import create_starter_game_state


def main(max_frames: Optional[int] = None) -> int:
    """Run the initial Pygame application."""
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)

    window = create_display(max_frames)
    scene = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.Font(None, 32)
    game_state = create_starter_game_state()

    try:
        return run_fixed_step(window, scene, font, game_state, max_frames=max_frames)
    finally:
        pygame.quit()


if __name__ == "__main__":
    raise SystemExit(main())
