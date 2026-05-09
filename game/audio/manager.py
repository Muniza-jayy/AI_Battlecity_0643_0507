"""Centralized audio manager for music, ambience, and sound effects."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import pygame  # type: ignore[import]

from game.audio.library import AMBIENCE_TRACKS, MUSIC_TRACKS, SFX_TRACKS
from game.audio.procedural import generate_ambience, generate_music, generate_sfx

if TYPE_CHECKING:
    from game.core.state import AppScreen, MatchOutcome


UI_CHANNEL = 0
PLAYER_CHANNEL = 1
ENEMY_CHANNEL = 2
IMPACT_CHANNEL = 3
AMBIENCE_CHANNEL_A = 4
AMBIENCE_CHANNEL_B = 5
MUSIC_CHANNEL = 6

SFX_CHANNELS: dict[str, int] = {
    "menu_hover": UI_CHANNEL,
    "menu_select": UI_CHANNEL,
    "pause": UI_CHANNEL,
    "unpause": UI_CHANNEL,
    "tank_move": PLAYER_CHANNEL,
    "shoot": PLAYER_CHANNEL,
    "bullet_hit": IMPACT_CHANNEL,
    "brick_break": IMPACT_CHANNEL,
    "steel_hit": IMPACT_CHANNEL,
    "player_hit": IMPACT_CHANNEL,
    "enemy_destroyed": ENEMY_CHANNEL,
    "eagle_destroyed": IMPACT_CHANNEL,
    "victory": UI_CHANNEL,
    "defeat": UI_CHANNEL,
}

SFX_COOLDOWNS_MS: dict[str, int] = {
    "menu_hover": 90,
    "menu_select": 120,
    "pause": 140,
    "unpause": 140,
    "tank_move": 180,
    "shoot": 100,
    "bullet_hit": 70,
    "brick_break": 90,
    "steel_hit": 90,
    "player_hit": 220,
    "enemy_destroyed": 180,
    "eagle_destroyed": 400,
    "victory": 600,
    "defeat": 600,
}

AMBIENCE_CHANNELS: dict[str, int] = {
    "menu_battlefield": AMBIENCE_CHANNEL_A,
    "menu_radio": AMBIENCE_CHANNEL_B,
    "gameplay_rumble": AMBIENCE_CHANNEL_A,
    "boss_tension": AMBIENCE_CHANNEL_B,
}


@dataclass
class AudioManager:
    """Safe wrapper around pygame.mixer with semantic playback methods."""

    enabled: bool = False
    muted: bool = False
    master_volume: float = 0.8
    music_volume: float = 0.24
    sfx_volume: float = 0.78
    ambience_volume: float = 0.1
    loaded_sfx: dict[str, pygame.mixer.Sound] = field(default_factory=dict)
    loaded_ambience: dict[str, pygame.mixer.Sound] = field(default_factory=dict)
    loaded_music_fallback: dict[str, pygame.mixer.Sound] = field(default_factory=dict)
    available_music: dict[str, Path] = field(default_factory=dict)
    current_music: str | None = None
    current_music_loops: int = -1
    current_ambience: dict[int, str | None] = field(
        default_factory=lambda: {AMBIENCE_CHANNEL_A: None, AMBIENCE_CHANNEL_B: None}
    )
    last_outcome: str | None = None
    last_sfx_ticks: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._initialize()

    def _initialize(self) -> None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(12)
        except pygame.error:
            self.enabled = False
            return

        self.enabled = True
        self._preload_assets()
        self._apply_bus_volumes()

    def _preload_assets(self) -> None:
        for sound_id, path in SFX_TRACKS.items():
            sound = self._load_sound(path)
            self.loaded_sfx[sound_id] = sound if sound is not None else generate_sfx(sound_id)

        for ambience_id, path in AMBIENCE_TRACKS.items():
            sound = self._load_sound(path)
            self.loaded_ambience[ambience_id] = sound if sound is not None else generate_ambience(ambience_id)

        for music_id, path in MUSIC_TRACKS.items():
            if path.exists():
                self.available_music[music_id] = path
            else:
                self.loaded_music_fallback[music_id] = generate_music(music_id)

    def _load_sound(self, path: Path) -> pygame.mixer.Sound | None:
        if not self.enabled or not path.exists():
            return None
        try:
            return pygame.mixer.Sound(str(path))
        except pygame.error:
            return None

    def _apply_bus_volumes(self) -> None:
        if not self.enabled:
            return

        effective_music = 0.0 if self.muted else self.master_volume * self.music_volume
        effective_sfx = 0.0 if self.muted else self.master_volume * self.sfx_volume
        effective_ambience = 0.0 if self.muted else self.master_volume * self.ambience_volume

        pygame.mixer.music.set_volume(effective_music)
        for sound in self.loaded_sfx.values():
            sound.set_volume(effective_sfx)
        for sound in self.loaded_ambience.values():
            sound.set_volume(effective_ambience)
        music_channel = pygame.mixer.Channel(MUSIC_CHANNEL)
        music_channel.set_volume(effective_music)

    def set_master_volume(self, value: float) -> None:
        self.master_volume = max(0.0, min(1.0, value))
        self._apply_bus_volumes()

    def set_music_volume(self, value: float) -> None:
        self.music_volume = max(0.0, min(1.0, value))
        self._apply_bus_volumes()

    def set_sfx_volume(self, value: float) -> None:
        self.sfx_volume = max(0.0, min(1.0, value))
        self._apply_bus_volumes()

    def set_ambience_volume(self, value: float) -> None:
        self.ambience_volume = max(0.0, min(1.0, value))
        self._apply_bus_volumes()

    def toggle_mute(self) -> None:
        self.muted = not self.muted
        self._apply_bus_volumes()

    def play_music(self, track_id: str, *, loops: int = -1) -> None:
        if not self.enabled or (self.current_music == track_id and self.current_music_loops == loops):
            return
        path = self.available_music.get(track_id)
        if path is not None:
            try:
                pygame.mixer.Channel(MUSIC_CHANNEL).stop()
                pygame.mixer.music.load(str(path))
                pygame.mixer.music.play(loops=loops)
                self.current_music = track_id
                self.current_music_loops = loops
                self._apply_bus_volumes()
                return
            except pygame.error:
                pass

        fallback = self.loaded_music_fallback.get(track_id)
        if fallback is None:
            return
        pygame.mixer.music.stop()
        channel = pygame.mixer.Channel(MUSIC_CHANNEL)
        channel.stop()
        channel.play(fallback, loops=loops)
        self.current_music = track_id
        self.current_music_loops = loops
        self._apply_bus_volumes()

    def stop_music(self) -> None:
        if not self.enabled:
            return
        pygame.mixer.music.stop()
        pygame.mixer.Channel(MUSIC_CHANNEL).stop()
        self.current_music = None
        self.current_music_loops = -1

    def play_sfx(self, sound_id: str) -> None:
        if not self.enabled or self.muted:
            return
        sound = self.loaded_sfx.get(sound_id)
        if sound is None:
            return
        now = pygame.time.get_ticks()
        cooldown = SFX_COOLDOWNS_MS.get(sound_id, 0)
        previous_tick = self.last_sfx_ticks.get(sound_id, -cooldown)
        if now - previous_tick < cooldown:
            return
        channel = pygame.mixer.Channel(SFX_CHANNELS.get(sound_id, IMPACT_CHANNEL))
        if channel.get_busy() and sound_id in {"menu_hover", "tank_move", "pause", "unpause"}:
            return
        channel.play(sound)
        self.last_sfx_ticks[sound_id] = now

    def play_ambience(self, ambience_id: str, *, loops: int = -1) -> None:
        if not self.enabled:
            return
        sound = self.loaded_ambience.get(ambience_id)
        channel_id = AMBIENCE_CHANNELS.get(ambience_id)
        if sound is None or channel_id is None:
            return
        if self.current_ambience[channel_id] == ambience_id:
            return
        channel = pygame.mixer.Channel(channel_id)
        channel.stop()
        channel.play(sound, loops=loops)
        self.current_ambience[channel_id] = ambience_id

    def stop_ambience(self, ambience_id: str | None = None) -> None:
        if not self.enabled:
            return
        if ambience_id is None:
            for channel_id in self.current_ambience:
                pygame.mixer.Channel(channel_id).stop()
                self.current_ambience[channel_id] = None
            return
        channel_id = AMBIENCE_CHANNELS.get(ambience_id)
        if channel_id is None:
            return
        pygame.mixer.Channel(channel_id).stop()
        self.current_ambience[channel_id] = None

    def stop_all(self) -> None:
        self.stop_music()
        self.stop_ambience()
        if self.enabled:
            pygame.mixer.stop()

    def set_screen_audio(self, screen: "AppScreen") -> None:
        """Prepare screen-based music/ambience routing for later use."""
        from game.core.state import AppScreen

        if screen is AppScreen.SPLASH:
            self.play_music("menu_theme")
            self.play_ambience("menu_battlefield")
            self.stop_ambience("menu_radio")
        elif screen is AppScreen.WELCOME:
            self.play_music("menu_theme")
            self.play_ambience("menu_battlefield")
            self.stop_ambience("menu_radio")
        elif screen in {AppScreen.OPTIONS, AppScreen.ABOUT, AppScreen.PAUSED, AppScreen.GAME_OVER}:
            self.play_music("menu_theme")
            self.play_ambience("menu_battlefield")
            self.stop_ambience("menu_radio")
            self.stop_ambience("gameplay_rumble")
            self.stop_ambience("boss_tension")

    def set_gameplay_audio(self, level_name: str) -> None:
        """Switch to gameplay or boss audio beds."""
        self.stop_ambience("menu_battlefield")
        self.stop_ambience("menu_radio")
        if level_name == "boss":
            self.play_music("boss_theme")
            self.play_ambience("gameplay_rumble")
            self.play_ambience("boss_tension")
        else:
            self.play_music("gameplay_theme")
            self.play_ambience("gameplay_rumble")
            self.stop_ambience("boss_tension")

    def set_outcome_audio(self, outcome: "MatchOutcome") -> None:
        """Play one-shot outcome music/SFX when the match ends."""
        outcome_id = str(outcome)
        if self.last_outcome == outcome_id:
            return
        self.last_outcome = outcome_id
        self.stop_ambience()
        if outcome_id == "victory":
            self.play_music("victory_theme", loops=0)
            self.play_sfx("victory")
        elif outcome_id == "defeat":
            self.play_music("defeat_theme", loops=0)
            self.play_sfx("defeat")

    def clear_outcome_latch(self) -> None:
        self.last_outcome = None
