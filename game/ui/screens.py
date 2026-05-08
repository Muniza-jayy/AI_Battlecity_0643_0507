"""Screen objects for the UI routing layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import pygame  # type: ignore[import]

from config.settings import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.state import AppScreen, AppState
from game.ui.widgets import Button, Panel


BG_BASE = (6, 10, 18)
GRID_COLOR = (39, 88, 104)
NEON_CYAN = (77, 241, 255)
NEON_RED = (255, 98, 122)
NEON_GOLD = (255, 204, 96)
SOFT_TEXT = (219, 233, 247)
MUTED_TEXT = (118, 146, 170)


class Screen(Protocol):
    def handle_event(self, event: pygame.event.Event, app_state: AppState) -> None: ...
    def update(self, app_state: AppState, dt_ms: int) -> None: ...
    def draw(self, surface: pygame.Surface, fonts: "UIFontPack", app_state: AppState) -> None: ...


@dataclass(frozen=True)
class UIFontPack:
    title: pygame.font.Font
    subtitle: pygame.font.Font
    body: pygame.font.Font
    button: pygame.font.Font
    small: pygame.font.Font


@dataclass
class WelcomeScreen:
    """Modern landing screen with animated cyber-grid background."""

    buttons: list[Button] = field(default_factory=list)
    pulse: float = 0.0

    def __post_init__(self) -> None:
        panel_x = SCREEN_WIDTH // 2 - 250
        start_y = 310
        width = 500
        height = 58
        gap = 18
        actions = [
            ("Start Game", NEON_CYAN, AppScreen.PLAYING),
            ("Game Options", NEON_GOLD, AppScreen.OPTIONS),
            ("About Project", NEON_RED, AppScreen.ABOUT),
            ("Quit", (255, 130, 155), AppScreen.GAME_OVER),
        ]
        self.buttons = []
        for index, (label, accent, target) in enumerate(actions):
            rect = pygame.Rect(panel_x, start_y + index * (height + gap), width, height)
            self.buttons.append(
                Button(
                    label=label,
                    rect=rect,
                    on_click=lambda: None,
                    accent_color=accent,
                    hover_color=(16, 32, 46),
                    action_id=target,
                )
            )

    def bind(self, app_state: AppState) -> None:
        for button in self.buttons:
            target = button.action_id
            if target is AppScreen.PLAYING:
                button.on_click = lambda app_state=app_state: self._start_game(app_state)
            elif target is AppScreen.OPTIONS:
                button.on_click = lambda app_state=app_state: self._change_screen(app_state, AppScreen.OPTIONS)
            elif target is AppScreen.ABOUT:
                button.on_click = lambda app_state=app_state: self._change_screen(app_state, AppScreen.ABOUT)
            else:
                button.on_click = lambda app_state=app_state: self._quit(app_state)

    def handle_event(self, event: pygame.event.Event, app_state: AppState) -> None:
        self.bind(app_state)
        for button in self.buttons:
            button.handle_event(event)

    def update(self, app_state: AppState, dt_ms: int) -> None:
        self.pulse = (self.pulse + dt_ms * 0.0014) % 6.283

    def draw(self, surface: pygame.Surface, fonts: UIFontPack, app_state: AppState) -> None:
        draw_cyber_background(surface, self.pulse)

        panel = Panel(pygame.Rect(SCREEN_WIDTH // 2 - 320, 78, 640, 640), border_color=NEON_CYAN)
        panel.draw(surface)

        title = fonts.title.render("Battle City AI", True, SOFT_TEXT)
        subtitle = fonts.subtitle.render("CSP  |  BFS  |  Greedy  |  A*  |  Minimax", True, NEON_CYAN)
        desc = fonts.body.render(
            "Playable AI battlefield with visible search behavior and tactical pressure.",
            True,
            MUTED_TEXT,
        )
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 158))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 212))
        desc_rect = desc.get_rect(center=(SCREEN_WIDTH // 2, 252))
        surface.blit(title, title_rect)
        surface.blit(subtitle, subtitle_rect)
        surface.blit(desc, desc_rect)

        draw_title_glow(surface, title_rect.inflate(80, 36), NEON_CYAN)

        for button in self.buttons:
            button.draw(surface, fonts.button)

        footer = fonts.small.render("Pygame desktop interface | Retro-futuristic command battlefield", True, MUTED_TEXT)
        surface.blit(footer, footer.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 42)))

    @staticmethod
    def _start_game(app_state: AppState) -> None:
        app_state.current_screen = AppScreen.PLAYING
        if app_state.game_state is not None:
            app_state.game_state.running = True

    @staticmethod
    def _change_screen(app_state: AppState, target: AppScreen) -> None:
        app_state.current_screen = target

    @staticmethod
    def _quit(app_state: AppState) -> None:
        app_state.running = False
        if app_state.game_state is not None:
            app_state.game_state.running = False


@dataclass
class PlaceholderScreen:
    """Temporary shell for screens implemented after the welcome pass."""

    title: str
    description: str
    accent_color: tuple[int, int, int]
    back_button: Button = field(init=False)

    def __post_init__(self) -> None:
        self.back_button = Button(
            label="Back",
            rect=pygame.Rect(72, SCREEN_HEIGHT - 108, 160, 52),
            on_click=lambda: None,
            accent_color=self.accent_color,
            hover_color=(18, 28, 40),
        )

    def handle_event(self, event: pygame.event.Event, app_state: AppState) -> None:
        self.back_button.on_click = lambda app_state=app_state: self._go_back(app_state)
        self.back_button.handle_event(event)

    def update(self, app_state: AppState, dt_ms: int) -> None:
        return

    def draw(self, surface: pygame.Surface, fonts: UIFontPack, app_state: AppState) -> None:
        draw_cyber_background(surface, 0.0)
        panel = Panel(pygame.Rect(78, 88, SCREEN_WIDTH - 156, SCREEN_HEIGHT - 176), border_color=self.accent_color)
        panel.draw(surface)
        title = fonts.title.render(self.title, True, SOFT_TEXT)
        desc = fonts.body.render(self.description, True, MUTED_TEXT)
        surface.blit(title, (118, 132))
        surface.blit(desc, (122, 204))
        self.back_button.draw(surface, fonts.button)

    @staticmethod
    def _go_back(app_state: AppState) -> None:
        app_state.current_screen = AppScreen.WELCOME


@dataclass
class ScreenRouter:
    """Owns screen objects and routes draw/update calls by state."""

    welcome: WelcomeScreen = field(default_factory=WelcomeScreen)
    options: PlaceholderScreen = field(default_factory=lambda: PlaceholderScreen(
        title="Game Options",
        description="Options screen shell is wired. Full controls come next.",
        accent_color=NEON_GOLD,
    ))
    about: PlaceholderScreen = field(default_factory=lambda: PlaceholderScreen(
        title="About Project",
        description="AI Lab project details screen shell is wired. Full content comes next.",
        accent_color=NEON_RED,
    ))

    def current(self, app_state: AppState) -> Screen | None:
        mapping: dict[AppScreen, Screen | None] = {
            AppScreen.WELCOME: self.welcome,
            AppScreen.OPTIONS: self.options,
            AppScreen.ABOUT: self.about,
            AppScreen.PLAYING: None,
            AppScreen.PAUSED: None,
            AppScreen.GAME_OVER: None,
        }
        return mapping[app_state.current_screen]


def draw_cyber_background(surface: pygame.Surface, pulse: float) -> None:
    surface.fill(BG_BASE)
    for y in range(SCREEN_HEIGHT):
        intensity = max(0, min(255, int(18 + y * 0.05)))
        pygame.draw.line(surface, (6, 10 + intensity // 8, 18 + intensity // 5), (0, y), (SCREEN_WIDTH, y))

    offset = int((pulse * 24) % 40)
    for x in range(-SCREEN_HEIGHT, SCREEN_WIDTH + SCREEN_HEIGHT, 40):
        color = (*GRID_COLOR,)
        pygame.draw.line(surface, color, (x + offset, 0), (x - 180 + offset, SCREEN_HEIGHT), width=1)
    for y in range(0, SCREEN_HEIGHT, 32):
        alpha = 28 + (y % 96)
        line_surface = pygame.Surface((SCREEN_WIDTH, 2), pygame.SRCALPHA)
        pygame.draw.line(line_surface, (*NEON_CYAN, min(80, alpha)), (0, 0), (SCREEN_WIDTH, 0), width=1)
        surface.blit(line_surface, (0, y))

    vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(vignette, (0, 0, 0, 88), vignette.get_rect(), width=80)
    surface.blit(vignette, (0, 0))


def draw_title_glow(surface: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
    glow = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (*color, 34), glow.get_rect())
    surface.blit(glow, rect.topleft)
