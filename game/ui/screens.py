"""Screen objects for the UI routing layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import pygame  # type: ignore[import]

from config.settings import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.state import AppScreen, AppState, MatchOutcome
from game.modes.level_flow import BOSS_LABEL, LEVEL_1_LABEL, LEVEL_2_LABEL, create_game_state_from_settings
from game.ui.widgets import Button, Panel


BG_BASE = (18, 20, 22)
BG_SHADE = (31, 28, 24)
GRID_COLOR = (78, 72, 58)
BRICK = (143, 75, 50)
BRICK_DARK = (91, 46, 33)
STEEL = (107, 116, 123)
STEEL_LIGHT = (157, 166, 171)
WATER = (52, 86, 108)
OLIVE = (103, 113, 69)
AMBER = (214, 169, 75)
WARNING = (176, 74, 63)
SOFT_TEXT = (230, 223, 207)
MUTED_TEXT = (162, 154, 139)


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
    """Battlefield-briefing landing screen with Battle City-inspired styling."""

    buttons: list[Button] = field(default_factory=list)
    pulse: float = 0.0

    def __post_init__(self) -> None:
        panel_x = SCREEN_WIDTH // 2 - 250
        start_y = 310
        width = 500
        height = 58
        gap = 18
        actions = [
            ("Start Operation", AMBER, AppScreen.PLAYING),
            ("Battle Options", OLIVE, AppScreen.OPTIONS),
            ("Project Brief", STEEL_LIGHT, AppScreen.ABOUT),
            ("Quit", WARNING, AppScreen.GAME_OVER),
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
                    hover_color=(50, 46, 40),
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
        draw_battlefield_background(surface, self.pulse)

        panel = Panel(
            pygame.Rect(64, 70, 560, 664),
            border_color=STEEL_LIGHT,
            fill_color=(25, 27, 28, 224),
        )
        panel.draw(surface)
        draw_brick_header_band(surface, panel.rect)
        draw_tactical_preview(surface, pygame.Rect(656, 86, 388, 360), self.pulse)
        draw_status_card(surface, fonts, pygame.Rect(656, 474, 388, 260))

        title = fonts.title.render("Battle City AI", True, SOFT_TEXT)
        subtitle = fonts.subtitle.render("CSP  |  BFS  |  GREEDY  |  A*  |  MINIMAX", True, AMBER)
        header = fonts.small.render("TACTICAL SEARCH SYSTEMS BRIEFING", True, OLIVE)
        desc = fonts.body.render(
            "Defend the eagle. Read the battlefield. Outmaneuver search-driven armor.",
            True,
            MUTED_TEXT,
        )
        title_rect = title.get_rect(topleft=(108, 130))
        header_rect = header.get_rect(topleft=(110, 108))
        subtitle_rect = subtitle.get_rect(topleft=(112, 210))
        desc_rect = desc.get_rect(topleft=(110, 258))
        surface.blit(header, header_rect)
        surface.blit(title, title_rect)
        surface.blit(subtitle, subtitle_rect)
        surface.blit(desc, desc_rect)

        draw_title_glow(surface, title_rect.inflate(40, 22), AMBER)
        draw_divider(surface, 110, 302, 468, BRICK)

        for button in self.buttons:
            button.draw(surface, fonts.button)

        footer = fonts.small.render("COMMAND CONSOLE | BATTLEFIELD THEATER 01", True, MUTED_TEXT)
        surface.blit(footer, footer.get_rect(midleft=(74, SCREEN_HEIGHT - 36)))

    @staticmethod
    def _start_game(app_state: AppState) -> None:
        app_state.game_state = create_game_state_from_settings(app_state.ui_settings)
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
            hover_color=(50, 46, 40),
        )

    def handle_event(self, event: pygame.event.Event, app_state: AppState) -> None:
        self.back_button.on_click = lambda app_state=app_state: self._go_back(app_state)
        self.back_button.handle_event(event)

    def update(self, app_state: AppState, dt_ms: int) -> None:
        return

    def draw(self, surface: pygame.Surface, fonts: UIFontPack, app_state: AppState) -> None:
        draw_battlefield_background(surface, 0.0)
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
class AboutScreen:
    """Project summary screen with working back navigation."""

    back_button: Button = field(init=False)

    def __post_init__(self) -> None:
        self.back_button = Button(
            label="Back",
            rect=pygame.Rect(72, SCREEN_HEIGHT - 108, 160, 52),
            on_click=lambda: None,
            accent_color=STEEL_LIGHT,
            hover_color=(50, 46, 40),
        )

    def handle_event(self, event: pygame.event.Event, app_state: AppState) -> None:
        self.back_button.on_click = lambda app_state=app_state: self._go_back(app_state)
        self.back_button.handle_event(event)

    def update(self, app_state: AppState, dt_ms: int) -> None:
        return

    def draw(self, surface: pygame.Surface, fonts: UIFontPack, app_state: AppState) -> None:
        draw_battlefield_background(surface, 0.0)
        panel = Panel(
            pygame.Rect(72, 82, SCREEN_WIDTH - 144, SCREEN_HEIGHT - 164),
            border_color=STEEL_LIGHT,
            fill_color=(24, 26, 28, 226),
        )
        panel.draw(surface)
        draw_brick_header_band(surface, panel.rect)

        title = fonts.title.render("Project Brief", True, SOFT_TEXT)
        subtitle = fonts.small.render("AI LAB FIELD DOSSIER", True, OLIVE)
        surface.blit(subtitle, (108, 112))
        surface.blit(title, (104, 136))

        summary_lines = (
            "Battle City AI is an AI Lab project focused on visible search behavior",
            "inside a human-playable tank-defense battlefield.",
        )
        for index, line in enumerate(summary_lines):
            text = fonts.body.render(line, True, MUTED_TEXT)
            surface.blit(text, (110, 240 + index * 42))

        mapping_title = fonts.subtitle.render("Tank / Algorithm Mapping", True, AMBER)
        surface.blit(mapping_title, (110, 352))
        mapping = (
            "Basic Tank   = BFS",
            "Fast Tank    = Greedy Best-First",
            "Armor Tank   = A*",
            "Boss Tank    = Minimax + Alpha-Beta",
        )
        for index, line in enumerate(mapping):
            text = fonts.body.render(line, True, SOFT_TEXT)
            surface.blit(text, (124, 408 + index * 44))

        self.back_button.draw(surface, fonts.button)

    @staticmethod
    def _go_back(app_state: AppState) -> None:
        app_state.current_screen = AppScreen.WELCOME


@dataclass
class OptionsScreen:
    """Interactive gameplay settings screen."""

    back_button: Button = field(init=False)
    level_buttons: list[Button] = field(default_factory=list)
    difficulty_buttons: list[Button] = field(default_factory=list)
    debug_toggle: Button = field(init=False)
    path_toggle: Button = field(init=False)

    def __post_init__(self) -> None:
        self.back_button = Button(
            label="Back",
            rect=pygame.Rect(72, SCREEN_HEIGHT - 108, 160, 52),
            on_click=lambda: None,
            accent_color=STEEL_LIGHT,
            hover_color=(50, 46, 40),
        )
        self.debug_toggle = Button(
            label="Debug Overlay: OFF",
            rect=pygame.Rect(120, 380, 360, 52),
            on_click=lambda: None,
            accent_color=OLIVE,
            hover_color=(50, 46, 40),
        )
        self.path_toggle = Button(
            label="Path Visualization: ON",
            rect=pygame.Rect(120, 448, 360, 52),
            on_click=lambda: None,
            accent_color=STEEL_LIGHT,
            hover_color=(50, 46, 40),
        )
        self.level_buttons = []
        for index, label in enumerate((LEVEL_1_LABEL, LEVEL_2_LABEL, BOSS_LABEL)):
            self.level_buttons.append(
                Button(
                    label=label,
                    rect=pygame.Rect(120, 172 + index * 62, 360, 48),
                    on_click=lambda: None,
                    accent_color=AMBER,
                    hover_color=(50, 46, 40),
                    action_id=label,
                )
            )
        self.difficulty_buttons = []
        for index, label in enumerate(("Easy", "Normal", "Hard")):
            self.difficulty_buttons.append(
                Button(
                    label=label,
                    rect=pygame.Rect(578 + index * 138, 174, 122, 48),
                    on_click=lambda: None,
                    accent_color=AMBER,
                    hover_color=(50, 46, 40),
                    action_id=label,
                )
            )

    def handle_event(self, event: pygame.event.Event, app_state: AppState) -> None:
        self.bind(app_state)
        self.back_button.handle_event(event)
        self.debug_toggle.handle_event(event)
        self.path_toggle.handle_event(event)
        for button in self.level_buttons:
            button.handle_event(event)
        for button in self.difficulty_buttons:
            button.handle_event(event)

    def update(self, app_state: AppState, dt_ms: int) -> None:
        self.debug_toggle.label = f"Debug Overlay: {'ON' if app_state.ui_settings.debug_overlay_enabled else 'OFF'}"
        self.path_toggle.label = f"Path Visualization: {'ON' if app_state.ui_settings.path_visualization_enabled else 'OFF'}"

    def draw(self, surface: pygame.Surface, fonts: UIFontPack, app_state: AppState) -> None:
        draw_battlefield_background(surface, 0.0)
        panel = Panel(
            pygame.Rect(72, 82, SCREEN_WIDTH - 144, SCREEN_HEIGHT - 164),
            border_color=STEEL_LIGHT,
            fill_color=(24, 26, 28, 226),
        )
        panel.draw(surface)
        draw_brick_header_band(surface, panel.rect)

        title = fonts.title.render("Battle Options", True, SOFT_TEXT)
        subtitle = fonts.small.render("MISSION PROFILE CONFIGURATION", True, OLIVE)
        surface.blit(subtitle, (108, 112))
        surface.blit(title, (104, 136))

        self._draw_section_label(surface, fonts, "Choose Level", 120, 168)
        self._draw_section_label(surface, fonts, "Difficulty", 578, 168)
        self._draw_section_label(surface, fonts, "Runtime Toggles", 120, 374)
        self._draw_section_label(surface, fonts, "Current Loadout", 578, 298)

        for button in self.level_buttons:
            style_selection_button(button, app_state.ui_settings.selected_level == button.action_id)
            button.draw(surface, fonts.button)
        for button in self.difficulty_buttons:
            style_selection_button(button, app_state.ui_settings.difficulty == button.action_id)
            button.draw(surface, fonts.button)

        self.debug_toggle.draw(surface, fonts.button)
        self.path_toggle.draw(surface, fonts.button)
        self.back_button.draw(surface, fonts.button)

        status_lines = (
            f"Selected level: {app_state.ui_settings.selected_level}",
            f"Difficulty: {app_state.ui_settings.difficulty}",
            f"Debug overlay: {'ON' if app_state.ui_settings.debug_overlay_enabled else 'OFF'}",
            f"Path preview: {'ON' if app_state.ui_settings.path_visualization_enabled else 'OFF'}",
            "Start the match from the welcome screen.",
        )
        for index, line in enumerate(status_lines):
            text = fonts.body.render(line, True, MUTED_TEXT)
            surface.blit(text, (580, 340 + index * 42))

    def bind(self, app_state: AppState) -> None:
        self.back_button.on_click = lambda app_state=app_state: self._go_back(app_state)
        self.debug_toggle.on_click = lambda app_state=app_state: self._toggle_debug(app_state)
        self.path_toggle.on_click = lambda app_state=app_state: self._toggle_paths(app_state)
        for button in self.level_buttons:
            label = button.action_id
            button.on_click = lambda label=label, app_state=app_state: self._set_level(app_state, str(label))
        for button in self.difficulty_buttons:
            label = button.action_id
            button.on_click = lambda label=label, app_state=app_state: self._set_difficulty(app_state, str(label))

    @staticmethod
    def _draw_section_label(surface: pygame.Surface, fonts: UIFontPack, label: str, x: int, y: int) -> None:
        text = fonts.small.render(label.upper(), True, AMBER)
        surface.blit(text, (x, y))

    @staticmethod
    def _go_back(app_state: AppState) -> None:
        app_state.current_screen = AppScreen.WELCOME

    @staticmethod
    def _set_level(app_state: AppState, label: str) -> None:
        app_state.ui_settings.selected_level = label

    @staticmethod
    def _set_difficulty(app_state: AppState, label: str) -> None:
        app_state.ui_settings.difficulty = label

    @staticmethod
    def _toggle_debug(app_state: AppState) -> None:
        app_state.ui_settings.debug_overlay_enabled = not app_state.ui_settings.debug_overlay_enabled

    @staticmethod
    def _toggle_paths(app_state: AppState) -> None:
        app_state.ui_settings.path_visualization_enabled = not app_state.ui_settings.path_visualization_enabled


@dataclass
class GameOverScreen:
    """End-of-match screen with working retry and back navigation."""

    retry_button: Button = field(init=False)
    back_button: Button = field(init=False)

    def __post_init__(self) -> None:
        self.retry_button = Button(
            label="Retry Mission",
            rect=pygame.Rect(SCREEN_WIDTH // 2 - 210, 430, 420, 56),
            on_click=lambda: None,
            accent_color=AMBER,
            hover_color=(50, 46, 40),
        )
        self.back_button = Button(
            label="Back to Menu",
            rect=pygame.Rect(SCREEN_WIDTH // 2 - 210, 504, 420, 56),
            on_click=lambda: None,
            accent_color=STEEL_LIGHT,
            hover_color=(50, 46, 40),
        )

    def handle_event(self, event: pygame.event.Event, app_state: AppState) -> None:
        self.retry_button.on_click = lambda app_state=app_state: self._retry(app_state)
        self.back_button.on_click = lambda app_state=app_state: self._back_to_menu(app_state)
        self.retry_button.handle_event(event)
        self.back_button.handle_event(event)

    def update(self, app_state: AppState, dt_ms: int) -> None:
        return

    def draw(self, surface: pygame.Surface, fonts: UIFontPack, app_state: AppState) -> None:
        draw_battlefield_background(surface, 0.0)
        panel = Panel(
            pygame.Rect(SCREEN_WIDTH // 2 - 280, 118, 560, 540),
            border_color=WARNING,
            fill_color=(26, 24, 24, 228),
        )
        panel.draw(surface)
        draw_brick_header_band(surface, panel.rect)

        outcome = "Mission Failed" if app_state.game_state and app_state.game_state.outcome is not MatchOutcome.VICTORY else "Mission Complete"
        title = fonts.title.render(outcome, True, SOFT_TEXT)
        subtitle = fonts.small.render("BATTLEFIELD REPORT", True, WARNING if "Failed" in outcome else AMBER)
        surface.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 186)))
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 246)))

        if app_state.game_state is not None:
            info = (
                f"Level: {app_state.game_state.level_name}",
                f"Score: {app_state.game_state.score}",
                f"Lives Remaining: {app_state.game_state.lives}",
            )
            for index, line in enumerate(info):
                text = fonts.body.render(line, True, MUTED_TEXT)
                surface.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, 330 + index * 42)))

        self.retry_button.draw(surface, fonts.button)
        self.back_button.draw(surface, fonts.button)

    @staticmethod
    def _retry(app_state: AppState) -> None:
        app_state.game_state = create_game_state_from_settings(app_state.ui_settings)
        app_state.current_screen = AppScreen.PLAYING

    @staticmethod
    def _back_to_menu(app_state: AppState) -> None:
        app_state.current_screen = AppScreen.WELCOME


@dataclass
class PauseScreen:
    """Paused-match control screen."""

    resume_button: Button = field(init=False)
    retry_button: Button = field(init=False)
    back_button: Button = field(init=False)

    def __post_init__(self) -> None:
        self.resume_button = Button(
            label="Resume",
            rect=pygame.Rect(SCREEN_WIDTH // 2 - 210, 356, 420, 56),
            on_click=lambda: None,
            accent_color=AMBER,
            hover_color=(50, 46, 40),
        )
        self.retry_button = Button(
            label="Restart Mission",
            rect=pygame.Rect(SCREEN_WIDTH // 2 - 210, 430, 420, 56),
            on_click=lambda: None,
            accent_color=OLIVE,
            hover_color=(50, 46, 40),
        )
        self.back_button = Button(
            label="Back to Menu",
            rect=pygame.Rect(SCREEN_WIDTH // 2 - 210, 504, 420, 56),
            on_click=lambda: None,
            accent_color=STEEL_LIGHT,
            hover_color=(50, 46, 40),
        )

    def handle_event(self, event: pygame.event.Event, app_state: AppState) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            self._resume(app_state)
            return
        self.resume_button.on_click = lambda app_state=app_state: self._resume(app_state)
        self.retry_button.on_click = lambda app_state=app_state: self._retry(app_state)
        self.back_button.on_click = lambda app_state=app_state: self._back_to_menu(app_state)
        self.resume_button.handle_event(event)
        self.retry_button.handle_event(event)
        self.back_button.handle_event(event)

    def update(self, app_state: AppState, dt_ms: int) -> None:
        return

    def draw(self, surface: pygame.Surface, fonts: UIFontPack, app_state: AppState) -> None:
        draw_battlefield_background(surface, 0.0)
        panel = Panel(
            pygame.Rect(SCREEN_WIDTH // 2 - 280, 118, 560, 540),
            border_color=AMBER,
            fill_color=(26, 24, 24, 228),
        )
        panel.draw(surface)
        draw_brick_header_band(surface, panel.rect)

        title = fonts.title.render("Mission Paused", True, SOFT_TEXT)
        subtitle = fonts.small.render("TACTICAL HOLD", True, AMBER)
        surface.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 186)))
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 246)))

        if app_state.game_state is not None:
            info = (
                f"Level: {app_state.game_state.level_name}",
                f"Score: {app_state.game_state.score}",
                f"Lives Remaining: {app_state.game_state.lives}",
            )
            for index, line in enumerate(info):
                text = fonts.body.render(line, True, MUTED_TEXT)
                surface.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, 330 + index * 42)))

        self.resume_button.draw(surface, fonts.button)
        self.retry_button.draw(surface, fonts.button)
        self.back_button.draw(surface, fonts.button)

    @staticmethod
    def _resume(app_state: AppState) -> None:
        if app_state.game_state is not None:
            app_state.game_state.paused = False
        app_state.current_screen = AppScreen.PLAYING

    @staticmethod
    def _retry(app_state: AppState) -> None:
        app_state.game_state = create_game_state_from_settings(app_state.ui_settings)
        app_state.current_screen = AppScreen.PLAYING

    @staticmethod
    def _back_to_menu(app_state: AppState) -> None:
        if app_state.game_state is not None:
            app_state.game_state.paused = False
        app_state.current_screen = AppScreen.WELCOME


@dataclass
class ScreenRouter:
    """Owns screen objects and routes draw/update calls by state."""

    welcome: WelcomeScreen = field(default_factory=WelcomeScreen)
    options: OptionsScreen = field(default_factory=OptionsScreen)
    about: AboutScreen = field(default_factory=AboutScreen)
    paused: PauseScreen = field(default_factory=PauseScreen)
    game_over: GameOverScreen = field(default_factory=GameOverScreen)

    def current(self, app_state: AppState) -> Screen | None:
        mapping: dict[AppScreen, Screen | None] = {
            AppScreen.WELCOME: self.welcome,
            AppScreen.OPTIONS: self.options,
            AppScreen.ABOUT: self.about,
            AppScreen.PLAYING: None,
            AppScreen.PAUSED: self.paused,
            AppScreen.GAME_OVER: self.game_over,
        }
        return mapping[app_state.current_screen]


def draw_battlefield_background(surface: pygame.Surface, pulse: float) -> None:
    surface.fill(BG_BASE)
    for y in range(SCREEN_HEIGHT):
        blend = min(255, max(0, int(24 + y * 0.08)))
        pygame.draw.line(surface, (BG_BASE[0] + blend // 5, BG_SHADE[1] + blend // 10, BG_SHADE[2]), (0, y), (SCREEN_WIDTH, y))

    for y in range(0, SCREEN_HEIGHT, 64):
        pygame.draw.rect(surface, (28, 28, 27), pygame.Rect(0, y, SCREEN_WIDTH, 2))

    offset = int((pulse * 14) % 48)
    for x in range(-SCREEN_HEIGHT, SCREEN_WIDTH + SCREEN_HEIGHT, 48):
        pygame.draw.line(surface, GRID_COLOR, (x + offset, 0), (x - 132 + offset, SCREEN_HEIGHT), width=1)
    for x in range(0, SCREEN_WIDTH, 48):
        line_surface = pygame.Surface((SCREEN_WIDTH, 2), pygame.SRCALPHA)
        pygame.draw.line(line_surface, (*STEEL, 24), (0, 0), (SCREEN_WIDTH, 0), width=1)
        surface.blit(line_surface, (0, x % SCREEN_HEIGHT))

    for x in range(0, SCREEN_WIDTH, 96):
        pygame.draw.line(surface, (54, 50, 42), (x, 0), (x, SCREEN_HEIGHT), width=1)

    dust = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for idx in range(0, SCREEN_WIDTH, 120):
        pygame.draw.circle(dust, (255, 210, 140, 8), (idx, 120 + (idx // 2) % 420), 90)
    surface.blit(dust, (0, 0))

    vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(vignette, (0, 0, 0, 98), vignette.get_rect(), width=90)
    surface.blit(vignette, (0, 0))


def draw_title_glow(surface: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
    glow = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (*color, 26), glow.get_rect())
    surface.blit(glow, rect.topleft)


def draw_divider(surface: pygame.Surface, x: int, y: int, width: int, color: tuple[int, int, int]) -> None:
    pygame.draw.line(surface, color, (x, y), (x + width, y), width=3)
    pygame.draw.line(surface, STEEL, (x, y + 5), (x + width, y + 5), width=1)


def draw_brick_header_band(surface: pygame.Surface, rect: pygame.Rect) -> None:
    band = pygame.Rect(rect.x, rect.y, rect.width, 36)
    pygame.draw.rect(surface, BRICK_DARK, band, border_top_left_radius=18, border_top_right_radius=18)
    for x in range(band.x + 8, band.right - 8, 42):
        pygame.draw.rect(surface, BRICK, pygame.Rect(x, band.y + 6, 34, 10), border_radius=2)
        pygame.draw.rect(surface, BRICK, pygame.Rect(x + 16, band.y + 19, 34, 10), border_radius=2)


def draw_tactical_preview(surface: pygame.Surface, rect: pygame.Rect, pulse: float) -> None:
    panel = Panel(rect, fill_color=(21, 24, 27, 224), border_color=STEEL)
    panel.draw(surface)
    inner = rect.inflate(-28, -28)
    pygame.draw.rect(surface, (17, 19, 20), inner, border_radius=10)
    cell = 28
    for y in range(inner.y, inner.bottom, cell):
        pygame.draw.line(surface, (52, 58, 61), (inner.x, y), (inner.right, y), width=1)
    for x in range(inner.x, inner.right, cell):
        pygame.draw.line(surface, (52, 58, 61), (x, inner.y), (x, inner.bottom), width=1)

    bricks = [
        (1, 1), (2, 1), (6, 2), (7, 2), (5, 5), (6, 5), (8, 7), (2, 8),
    ]
    steels = [(4, 2), (4, 3), (9, 4), (3, 7)]
    waters = [(1, 6), (2, 6), (7, 8)]
    forests = [(9, 1), (10, 1), (10, 6)]
    for gx, gy in bricks:
        draw_tile_block(surface, inner, gx, gy, BRICK, BRICK_DARK)
    for gx, gy in steels:
        draw_tile_block(surface, inner, gx, gy, STEEL_LIGHT, STEEL)
    for gx, gy in waters:
        draw_tile_block(surface, inner, gx, gy, WATER, (35, 60, 78))
    for gx, gy in forests:
        draw_tile_block(surface, inner, gx, gy, OLIVE, (69, 80, 46))

    player = (inner.x + cell * 5 + cell // 2, inner.y + cell * 10 + cell // 2)
    boss = (inner.x + cell * 8 + cell // 2, inner.y + cell * 2 + cell // 2)
    eagle = (inner.x + cell * 5 + cell // 2, inner.y + cell * 9 + cell // 2)
    draw_tank_marker(surface, player, SOFT_TEXT, (86, 72, 38))
    draw_tank_marker(surface, boss, WARNING, (81, 32, 28))
    pygame.draw.rect(surface, (214, 188, 103), pygame.Rect(eagle[0] - 8, eagle[1] - 8, 16, 16), border_radius=3)
    sweep_x = inner.x + int((pulse * 32) % max(1, inner.width))
    pygame.draw.line(surface, (*AMBER, 120), (sweep_x, inner.y), (sweep_x - 48, inner.bottom), width=2)


def draw_tile_block(surface: pygame.Surface, inner: pygame.Rect, gx: int, gy: int, fill: tuple[int, int, int], accent: tuple[int, int, int]) -> None:
    cell = 28
    rect = pygame.Rect(inner.x + gx * cell + 4, inner.y + gy * cell + 4, cell - 8, cell - 8)
    pygame.draw.rect(surface, fill, rect, border_radius=4)
    pygame.draw.rect(surface, accent, rect, width=1, border_radius=4)


def draw_tank_marker(surface: pygame.Surface, center: tuple[int, int], fill: tuple[int, int, int], accent: tuple[int, int, int]) -> None:
    rect = pygame.Rect(0, 0, 18, 18)
    rect.center = center
    pygame.draw.rect(surface, fill, rect, border_radius=4)
    pygame.draw.rect(surface, accent, rect, width=2, border_radius=4)
    pygame.draw.line(surface, accent, center, (center[0], center[1] - 14), width=3)


def draw_status_card(surface: pygame.Surface, fonts: UIFontPack, rect: pygame.Rect) -> None:
    panel = Panel(rect, fill_color=(24, 26, 29, 226), border_color=BRICK)
    panel.draw(surface)
    title = fonts.subtitle.render("BATTLEFIELD BRIEF", True, SOFT_TEXT)
    lines = (
        "Primary objective: Defend the Eagle",
        "Threat classes: Basic / Fast / Armor / Boss",
        "Algorithms are visible through battlefield behavior",
        "Mission tone: tactical, grounded, arcade warfare",
    )
    surface.blit(title, (rect.x + 24, rect.y + 22))
    for index, line in enumerate(lines):
        text = fonts.small.render(line, True, MUTED_TEXT)
        surface.blit(text, (rect.x + 26, rect.y + 76 + index * 32))


def style_selection_button(button: Button, selected: bool) -> None:
    if selected:
        button.base_color = (72, 59, 38)
        button.border_color = AMBER
        button.text_color = SOFT_TEXT
    else:
        button.base_color = (38, 42, 45)
        button.border_color = (144, 116, 76)
        button.text_color = (233, 225, 208)
