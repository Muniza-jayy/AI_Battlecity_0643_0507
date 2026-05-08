"""Reusable UI widgets for the screen system."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pygame  # type: ignore[import]


Color = tuple[int, int, int]


@dataclass
class Button:
    """Simple neon-styled button."""

    label: str
    rect: pygame.Rect
    on_click: Callable[[], None]
    accent_color: Color
    hover_color: Color
    base_color: Color = (15, 20, 30)
    border_color: Color = (76, 241, 255)
    text_color: Color = (236, 244, 255)
    hovered: bool = False
    action_id: str | None = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        fill = self.hover_color if self.hovered else self.base_color
        glow = self.accent_color if self.hovered else self.border_color

        glow_rect = self.rect.inflate(12, 12)
        glow_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*glow, 52), glow_surface.get_rect(), border_radius=18)
        surface.blit(glow_surface, glow_rect.topleft)

        pygame.draw.rect(surface, fill, self.rect, border_radius=16)
        pygame.draw.rect(surface, glow, self.rect, width=2, border_radius=16)

        label_surface = font.render(self.label, True, self.text_color)
        label_rect = label_surface.get_rect(center=self.rect.center)
        surface.blit(label_surface, label_rect)


@dataclass
class Panel:
    """Framed translucent panel."""

    rect: pygame.Rect
    fill_color: tuple[int, int, int, int] = (8, 12, 20, 208)
    border_color: Color = (59, 222, 255)

    def draw(self, surface: pygame.Surface) -> None:
        panel_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, self.fill_color, panel_surface.get_rect(), border_radius=28)
        pygame.draw.rect(panel_surface, (*self.border_color, 220), panel_surface.get_rect(), width=2, border_radius=28)
        surface.blit(panel_surface, self.rect.topleft)
