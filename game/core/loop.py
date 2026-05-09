"""Early game-loop helpers for input, update, and render phases."""

from __future__ import annotations

import os
import random
from typing import Optional

import pygame  # type: ignore[import]

from config.settings import (
    BACKGROUND_COLOR,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WINDOW_TITLE,
)
from config.balance import MAX_ACTIVE_ENEMIES
from game.entities.bullet import spawn_bullet_from_tank
from game.entities.enemy import (
    enemy_requires_replan,
    fire_enemy_bullet,
    move_enemy,
    tick_enemy_decision_timer,
    try_spawn_enemy,
    update_basic_enemy_decision,
)
from game.entities.player import move_player
from game.entities.tank import Direction, Tank
from game.core.state import AppScreen, AppState, GameState, InputState, MatchOutcome
from game.modes.level_flow import STANDARD_PROGRESS_LEVELS, advance_to_boss_level
from game.modes.simulation_mode import regenerate_simulation_level
from game.ui.renderer import draw_scene
from game.ui.screens import ScreenRouter, UIFontPack
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


def build_input_state(events: list[pygame.event.Event]) -> InputState:
    """Build an input snapshot from a provided event batch."""
    input_state = InputState()

    for event in events:
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
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            input_state.toggle_debug_overlay_requested = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
            input_state.regenerate_map_requested = True

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


def remap_events_to_scene(events: list[pygame.event.Event], viewport: pygame.Rect) -> list[pygame.event.Event]:
    """Convert window-space mouse events into fixed-scene coordinates."""
    remapped: list[pygame.event.Event] = []
    scale_x = SCREEN_WIDTH / max(1, viewport.width)
    scale_y = SCREEN_HEIGHT / max(1, viewport.height)
    for event in events:
        if event.type not in {pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP}:
            remapped.append(event)
            continue

        pos = getattr(event, "pos", None)
        if pos is None:
            remapped.append(event)
            continue

        scene_pos = scene_point_from_window_point(pos, viewport, scale_x, scale_y)
        if event.type == pygame.MOUSEMOTION:
            rel = getattr(event, "rel", (0, 0))
            remapped.append(pygame.event.Event(event.type, {"pos": scene_pos, "rel": rel, "buttons": event.buttons}))
        else:
            remapped.append(pygame.event.Event(event.type, {"pos": scene_pos, "button": event.button}))
    return remapped


def scene_point_from_window_point(
    pos: tuple[int, int],
    viewport: pygame.Rect,
    scale_x: float,
    scale_y: float,
) -> tuple[int, int]:
    if not viewport.collidepoint(pos):
        return (-10_000, -10_000)
    scene_x = int((pos[0] - viewport.x) * scale_x)
    scene_y = int((pos[1] - viewport.y) * scale_y)
    return (scene_x, scene_y)


def collect_input() -> InputState:
    """Read input events for the current frame."""
    return build_input_state(list(pygame.event.get()))


def update_game_state(game_state: GameState, input_state: InputState, audio_manager=None) -> None:
    """Apply frame input to the game state."""
    if input_state.quit_requested:
        game_state.running = False
        return

    if input_state.toggle_debug_overlay_requested:
        game_state.debug_overlay_enabled = not game_state.debug_overlay_enabled

    if input_state.regenerate_map_requested:
        regenerate_simulation_level(game_state, seed=random.randint(1, 999_999))

    if game_state.outcome is not MatchOutcome.ACTIVE:
        game_state.frame_count += 1
        return

    if input_state.toggle_pause_requested:
        game_state.paused = not game_state.paused
        if audio_manager is not None:
            audio_manager.play_sfx("pause" if game_state.paused else "unpause")

    if not game_state.paused:
        spawn_waiting_enemies(game_state)
        move_player(
            game_state.player,
            input_state.movement_direction,
            game_state.tile_map,
            blocking_tanks=tuple(game_state.active_enemies),
        )
        if input_state.movement_direction is not None and audio_manager is not None:
            audio_manager.play_sfx("tank_move")
        if input_state.fire_requested and game_state.player_bullet is None:
            game_state.player_bullet = spawn_bullet_from_tank(game_state.player, owner="player")
            if audio_manager is not None:
                audio_manager.play_sfx("shoot")
        if game_state.player_bullet is not None:
            impact = advance_bullet(
                game_state.player_bullet,
                game_state.tile_map,
                enemies=tuple(game_state.active_enemies),
            )
            if impact.hit is BulletHit.EAGLE:
                game_state.eagle_destroyed = True
                if audio_manager is not None:
                    audio_manager.play_sfx("bullet_hit")
                    audio_manager.play_sfx("eagle_destroyed")
            elif impact.hit is BulletHit.ENEMY and impact.enemy_id is not None:
                if damage_enemy(game_state, impact.enemy_id):
                    game_state.score += 100
                    game_state.enemies_remaining = max(0, game_state.enemies_remaining - 1)
                    if audio_manager is not None:
                        audio_manager.play_sfx("enemy_destroyed")
            elif impact.hit is BulletHit.BRICK and audio_manager is not None:
                audio_manager.play_sfx("bullet_hit")
                audio_manager.play_sfx("brick_break")
            elif impact.hit is BulletHit.STEEL and audio_manager is not None:
                audio_manager.play_sfx("bullet_hit")
                audio_manager.play_sfx("steel_hit")
            if not game_state.player_bullet.active:
                game_state.player_bullet = None

        update_enemies(game_state, audio_manager=audio_manager)
        evaluate_match_state(game_state)

    game_state.frame_count += 1


def evaluate_match_state(game_state: GameState) -> None:
    """Resolve current win/lose conditions from the canonical game state."""
    if game_state.eagle_destroyed or game_state.lives <= 0:
        game_state.outcome = MatchOutcome.DEFEAT
        return

    if game_state.enemy_count_target > 0 and game_state.enemies_remaining <= 0:
        if game_state.level_name in STANDARD_PROGRESS_LEVELS:
            advance_to_boss_level(game_state)
            return
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
        game_state.active_enemies,
        game_state.lives,
        game_state.score,
        game_state.enemies_remaining,
        game_state.eagle_destroyed,
        game_state.outcome,
        game_state.paused,
        game_state.level_name,
        game_state.debug_overlay_enabled,
        game_state.path_visualization_enabled,
        game_state.tile_map.revision,
        len(game_state.enemy_spawn_queue),
        game_state.generated_seed,
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


def run_application_loop(
    window: pygame.Surface,
    scene: pygame.Surface,
    fonts: UIFontPack,
    app_state: AppState,
    max_frames: Optional[int] = None,
) -> int:
    """Run the top-level application loop with screen routing."""
    clock = pygame.time.Clock()
    router = ScreenRouter()
    app_frame_count = 0
    last_audio_signature: tuple | None = None

    while app_state.running:
        dt_ms = clock.tick(FPS)
        events = list(pygame.event.get())
        if any(event.type == pygame.QUIT for event in events):
            app_state.running = False
            break

        resized = next((event.size for event in events if event.type == pygame.VIDEORESIZE), None)
        if resized is not None:
            window = pygame.display.set_mode(resized, pygame.RESIZABLE)

        window_width, window_height = window.get_size()
        viewport = compute_letterbox(SCREEN_WIDTH, SCREEN_HEIGHT, window_width, window_height)
        scene_events = remap_events_to_scene(events, viewport)

        audio_signature = (
            app_state.current_screen,
            app_state.game_state.level_name if app_state.game_state is not None else None,
            app_state.game_state.outcome if app_state.game_state is not None else None,
        )
        if app_state.audio_manager is not None and audio_signature != last_audio_signature:
            sync_audio_state(app_state)
            last_audio_signature = audio_signature

        active_screen = router.current(app_state)
        if active_screen is not None:
            for event in scene_events:
                active_screen.handle_event(event, app_state)
            active_screen.update(app_state, dt_ms)
            active_screen.draw(scene, fonts, app_state)
        else:
            if app_state.game_state is None:
                raise RuntimeError("PLAYING state requires an active GameState")
            input_state = build_input_state(events)
            update_game_state(app_state.game_state, input_state, audio_manager=app_state.audio_manager)
            if input_state.quit_requested:
                app_state.running = False
            if app_state.game_state.paused:
                app_state.current_screen = AppScreen.PAUSED
            render_frame(window, scene, fonts.body, app_state.game_state)
            if app_state.game_state.outcome is not MatchOutcome.ACTIVE:
                app_state.current_screen = AppScreen.GAME_OVER

        if active_screen is not None:
            window.fill(BACKGROUND_COLOR)
            scaled_scene = pygame.transform.smoothscale(scene, viewport.size)
            window.blit(scaled_scene, viewport.topleft)
            pygame.display.flip()

        if max_frames is not None:
            app_frame_count += 1
            if app_frame_count >= max_frames:
                app_state.running = False

    return 0


def sync_audio_state(app_state: AppState) -> None:
    """Keep music and ambience aligned to the current screen and match state."""
    audio = app_state.audio_manager
    if audio is None:
        return

    if app_state.current_screen in {AppScreen.SPLASH, AppScreen.WELCOME, AppScreen.OPTIONS, AppScreen.ABOUT}:
        audio.clear_outcome_latch()
        audio.set_screen_audio(app_state.current_screen)
        return

    if app_state.current_screen in {AppScreen.PLAYING, AppScreen.PAUSED} and app_state.game_state is not None:
        audio.clear_outcome_latch()
        audio.set_gameplay_audio(app_state.game_state.level_name)
        return

    if app_state.current_screen is AppScreen.GAME_OVER and app_state.game_state is not None:
        audio.set_outcome_audio(app_state.game_state.outcome)


def spawn_waiting_enemies(game_state: GameState) -> None:
    """Spawn queued enemies into available spawn points up to the active cap."""
    while len(game_state.active_enemies) < MAX_ACTIVE_ENEMIES and game_state.enemy_spawn_queue:
        spawned = False
        for spawn_tile in game_state.tile_map.enemy_spawns:
            enemy = try_spawn_enemy(
                game_state.next_enemy_id,
                game_state.enemy_spawn_queue[0],
                spawn_tile,
                game_state.tile_map,
                blocking_tanks=tuple([game_state.player, *game_state.active_enemies]),
            )
            if enemy is None:
                continue
            game_state.active_enemies.append(enemy)
            game_state.enemy_spawn_queue.pop(0)
            game_state.next_enemy_id += 1
            spawned = True
            break
        if not spawned:
            return


def update_enemies(game_state: GameState, audio_manager=None) -> None:
    """Update enemy decisions, movement, and bullets."""
    for enemy in list(game_state.active_enemies):
        if enemy_requires_replan(enemy, game_state.tile_map):
            enemy.frames_until_decision = 0
        if tick_enemy_decision_timer(enemy):
            should_fire = update_basic_enemy_decision(
                enemy,
                game_state.tile_map,
                game_state.player,
                player_lives=game_state.lives,
            )
            if should_fire:
                fire_enemy_bullet(enemy)
                if audio_manager is not None:
                    audio_manager.play_sfx("shoot")

        blocking_tanks: tuple[Tank, ...] = tuple(
            tank for tank in [game_state.player, *game_state.active_enemies] if tank is not enemy
        )
        move_enemy(enemy, game_state.tile_map, blocking_tanks=blocking_tanks)

        if enemy.bullet is not None:
            impact = advance_bullet(enemy.bullet, game_state.tile_map, player=game_state.player)
            if impact.hit is BulletHit.PLAYER:
                game_state.lives = max(0, game_state.lives - 1)
                if audio_manager is not None:
                    audio_manager.play_sfx("player_hit")
            elif impact.hit is BulletHit.EAGLE:
                game_state.eagle_destroyed = True
                if audio_manager is not None:
                    audio_manager.play_sfx("bullet_hit")
                    audio_manager.play_sfx("eagle_destroyed")
            elif impact.hit is BulletHit.BRICK and audio_manager is not None:
                audio_manager.play_sfx("bullet_hit")
                audio_manager.play_sfx("brick_break")
            elif impact.hit is BulletHit.STEEL and audio_manager is not None:
                audio_manager.play_sfx("bullet_hit")
                audio_manager.play_sfx("steel_hit")
            if not enemy.bullet.active:
                enemy.bullet = None


def damage_enemy(game_state: GameState, enemy_id: int) -> bool:
    """Apply one hit to an enemy and return whether it was destroyed."""
    for enemy in game_state.active_enemies:
        if enemy.enemy_id != enemy_id:
            continue
        enemy.hit_points -= 1
        if enemy.hit_points > 0:
            return False
        break
    else:
        return False

    game_state.active_enemies = [
        enemy for enemy in game_state.active_enemies if enemy.enemy_id != enemy_id
    ]
    return True
