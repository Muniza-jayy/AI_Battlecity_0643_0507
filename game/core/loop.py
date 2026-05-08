"""Early game-loop helpers for input, update, and render phases."""

from __future__ import annotations

import os
from typing import Optional

import pygame  # type: ignore[import]

from config.settings import (
    BACKGROUND_COLOR,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WINDOW_TITLE,
)
from game.entities.bullet import spawn_bullet_from_tank
from game.entities.player import move_player
from game.entities.tank import Direction
from game.core.state import GameState, InputState, MatchOutcome
from game.ui.renderer import draw_scene
from game.world.projectiles import BulletHit, advance_bullet


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


def collect_input() -> InputState:
    """Read input events for the current frame."""
    input_state = InputState()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            input_state.quit_requested = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            input_state.quit_requested = True
        elif event.type == pygame.VIDEORESIZE:
            input_state.resized_to = event.size
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            input_state.toggle_pause_requested = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            input_state.fire_requested = True

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_UP] or pressed[pygame.K_w]:
        input_state.movement_direction = Direction.UP
    elif pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
        input_state.movement_direction = Direction.DOWN
    elif pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
        input_state.movement_direction = Direction.LEFT
    elif pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
        input_state.movement_direction = Direction.RIGHT

    return input_state


def update_game_state(game_state: GameState, input_state: InputState) -> None:
    """Apply frame input to the game state."""
    if input_state.quit_requested:
        game_state.running = False
        return

    if game_state.outcome is not MatchOutcome.ACTIVE:
        game_state.frame_count += 1
        return

    if input_state.toggle_pause_requested:
        game_state.paused = not game_state.paused

    if not game_state.paused:
        move_player(game_state.player, input_state.movement_direction, game_state.tile_map)
        if input_state.fire_requested and game_state.player_bullet is None:
            game_state.player_bullet = spawn_bullet_from_tank(game_state.player)
        if game_state.player_bullet is not None:
            hit = advance_bullet(game_state.player_bullet, game_state.tile_map)
            if hit is BulletHit.EAGLE:
                game_state.eagle_destroyed = True
            if not game_state.player_bullet.active:
                game_state.player_bullet = None

        evaluate_match_state(game_state)

    game_state.frame_count += 1


def evaluate_match_state(game_state: GameState) -> None:
    """Resolve current win/lose conditions from the canonical game state."""
    if game_state.eagle_destroyed or game_state.lives <= 0:
        game_state.outcome = MatchOutcome.DEFEAT
        return

    if game_state.enemy_count_target > 0 and game_state.enemies_remaining <= 0:
        game_state.outcome = MatchOutcome.VICTORY


def render_frame(
    window: pygame.Surface,
    scene: pygame.Surface,
    font: pygame.font.Font,
    game_state: GameState,
) -> None:
    """Render the current game scene and present it with letterboxing."""
    draw_scene(
        scene,
        font,
        game_state.tile_map,
        game_state.player,
        game_state.player_bullet,
        game_state.lives,
        game_state.score,
        game_state.enemies_remaining,
        game_state.eagle_destroyed,
        game_state.outcome,
        game_state.paused,
    )

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


def run_fixed_step(
    window: pygame.Surface,
    scene: pygame.Surface,
    font: pygame.font.Font,
    game_state: GameState,
    max_frames: Optional[int] = None,
) -> int:
    """Run the main fixed-step loop."""
    clock = pygame.time.Clock()

    while game_state.running:
        input_state = collect_input()
        if input_state.resized_to is not None:
            window = pygame.display.set_mode(input_state.resized_to, pygame.RESIZABLE)

        update_game_state(game_state, input_state)
        render_frame(window, scene, font, game_state)

        clock.tick(FPS)
        if max_frames is not None and game_state.frame_count >= max_frames:
            game_state.running = False

    return 0
