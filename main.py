"""Bootstrap entry point for the Battle City AI project."""

from __future__ import annotations

from typing import Optional

import pygame  # type: ignore[import]

from config.levels import STARTER_ENEMY_POOL
from config.settings import SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE
from game.core.loop import create_display, run_fixed_step
from game.core.state import GameState
from game.entities.player import spawn_player
from game.world.map_loader import load_starter_level


def main(max_frames: Optional[int] = None) -> int:
    """Run the initial Pygame application."""
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)

    window = create_display(max_frames)
    scene = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.Font(None, 32)
    tile_map = load_starter_level()
    game_state = GameState(
        tile_map=tile_map,
        player=spawn_player(tile_map.player_spawn),
        enemies_remaining=len(STARTER_ENEMY_POOL),
        enemy_count_target=len(STARTER_ENEMY_POOL),
    )

    try:
        return run_fixed_step(window, scene, font, game_state, max_frames=max_frames)
    finally:
        pygame.quit()


if __name__ == "__main__":
    raise SystemExit(main())
