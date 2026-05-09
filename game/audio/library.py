"""Semantic audio manifest for music, ambience, and sound effects."""

from __future__ import annotations

from pathlib import Path


ASSETS_AUDIO_ROOT = Path(__file__).resolve().parents[2] / "assets" / "audio"
MUSIC_ROOT = ASSETS_AUDIO_ROOT / "music"
SFX_ROOT = ASSETS_AUDIO_ROOT / "sfx"
AMBIENCE_ROOT = ASSETS_AUDIO_ROOT / "ambience"

MUSIC_TRACKS: dict[str, Path] = {
    "menu_theme": MUSIC_ROOT / "menu_theme.ogg",
    "gameplay_theme": MUSIC_ROOT / "gameplay_theme.ogg",
    "boss_theme": MUSIC_ROOT / "boss_theme.ogg",
    "victory_theme": MUSIC_ROOT / "victory_theme.ogg",
    "defeat_theme": MUSIC_ROOT / "defeat_theme.ogg",
}

AMBIENCE_TRACKS: dict[str, Path] = {
    "menu_battlefield": AMBIENCE_ROOT / "menu_battlefield.ogg",
    "menu_radio": AMBIENCE_ROOT / "menu_radio.ogg",
    "gameplay_rumble": AMBIENCE_ROOT / "gameplay_rumble.ogg",
    "boss_tension": AMBIENCE_ROOT / "boss_tension.ogg",
}

SFX_TRACKS: dict[str, Path] = {
    "menu_hover": SFX_ROOT / "menu_hover.wav",
    "menu_select": SFX_ROOT / "menu_select.wav",
    "pause": SFX_ROOT / "pause.wav",
    "unpause": SFX_ROOT / "unpause.wav",
    "tank_move": SFX_ROOT / "tank_move.wav",
    "shoot": SFX_ROOT / "shoot.wav",
    "bullet_hit": SFX_ROOT / "bullet_hit.wav",
    "brick_break": SFX_ROOT / "brick_break.wav",
    "steel_hit": SFX_ROOT / "steel_hit.wav",
    "player_hit": SFX_ROOT / "player_hit.wav",
    "enemy_destroyed": SFX_ROOT / "enemy_destroyed.wav",
    "eagle_destroyed": SFX_ROOT / "eagle_destroyed.wav",
    "victory": SFX_ROOT / "victory.wav",
    "defeat": SFX_ROOT / "defeat.wav",
}

