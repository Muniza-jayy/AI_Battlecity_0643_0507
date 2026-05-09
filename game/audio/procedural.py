"""Procedural fallback sound generation for the audio system."""

from __future__ import annotations

import math
import random
from array import array

import pygame  # type: ignore[import]


SAMPLE_RATE = 22_050
MAX_AMPLITUDE = 24_000


def _clamp_sample(value: float) -> int:
    return max(-32_767, min(32_767, int(value)))


def _make_sound(samples: array[int]) -> pygame.mixer.Sound:
    return pygame.mixer.Sound(buffer=samples.tobytes())


def _tone(
    frequency: float,
    duration: float,
    *,
    volume: float = 0.35,
    waveform: str = "sine",
    attack: float = 0.01,
    decay: float = 0.05,
) -> array[int]:
    frames = max(1, int(SAMPLE_RATE * duration))
    data = array("h")
    for index in range(frames):
        t = index / SAMPLE_RATE
        phase = 2.0 * math.pi * frequency * t
        if waveform == "square":
            raw = 1.0 if math.sin(phase) >= 0 else -1.0
        elif waveform == "triangle":
            raw = 2.0 * abs(2.0 * ((frequency * t) % 1.0) - 1.0) - 1.0
        else:
            raw = math.sin(phase)

        env = 1.0
        if t < attack:
            env = t / max(attack, 1e-6)
        elif t > duration - decay:
            env = max(0.0, (duration - t) / max(decay, 1e-6))
        data.append(_clamp_sample(raw * volume * env * MAX_AMPLITUDE))
    return data


def _noise(duration: float, *, volume: float = 0.2, lowpass: float = 0.6) -> array[int]:
    frames = max(1, int(SAMPLE_RATE * duration))
    data = array("h")
    previous = 0.0
    for _ in range(frames):
        target = random.uniform(-1.0, 1.0)
        previous = previous * lowpass + target * (1.0 - lowpass)
        data.append(_clamp_sample(previous * volume * MAX_AMPLITUDE))
    return data


def _mix(*tracks: array[int]) -> array[int]:
    length = max((len(track) for track in tracks), default=0)
    mixed = array("h")
    for index in range(length):
        sample = 0.0
        for track in tracks:
            if index < len(track):
                sample += track[index]
        mixed.append(_clamp_sample(sample))
    return mixed


def _append(*tracks: array[int]) -> array[int]:
    combined = array("h")
    for track in tracks:
        combined.extend(track)
    return combined


def _silence(duration: float) -> array[int]:
    return array("h", [0] * max(1, int(SAMPLE_RATE * duration)))


def _pulse(
    frequency: float,
    duration: float,
    *,
    volume: float = 0.2,
    waveform: str = "square",
    gap: float = 0.02,
) -> array[int]:
    tone = _tone(frequency, duration, volume=volume, waveform=waveform, attack=0.004, decay=duration * 0.45)
    return _append(tone, _silence(gap))


def generate_sfx(sound_id: str) -> pygame.mixer.Sound:
    if sound_id == "menu_hover":
        return _make_sound(_append(_tone(680, 0.03, volume=0.18), _tone(860, 0.03, volume=0.14)))
    if sound_id == "menu_select":
        return _make_sound(_append(_tone(540, 0.05, volume=0.22), _tone(740, 0.08, volume=0.18)))
    if sound_id == "pause":
        return _make_sound(_append(_tone(420, 0.04, volume=0.22), _tone(300, 0.05, volume=0.16)))
    if sound_id == "unpause":
        return _make_sound(_append(_tone(320, 0.04, volume=0.18), _tone(460, 0.05, volume=0.22)))
    if sound_id == "tank_move":
        return _make_sound(
            _mix(
                _pulse(74, 0.05, volume=0.08, waveform="triangle", gap=0.015),
                _pulse(58, 0.05, volume=0.06, waveform="triangle", gap=0.015),
            )
        )
    if sound_id == "shoot":
        return _make_sound(
            _append(
                _tone(135, 0.03, volume=0.28, waveform="square", attack=0.001, decay=0.02),
                _noise(0.045, volume=0.08, lowpass=0.55),
                _tone(92, 0.025, volume=0.08, waveform="triangle"),
            )
        )
    if sound_id == "bullet_hit":
        return _make_sound(_append(_tone(920, 0.018, volume=0.12), _noise(0.03, volume=0.05, lowpass=0.35)))
    if sound_id == "brick_break":
        return _make_sound(_append(_noise(0.055, volume=0.08, lowpass=0.38), _tone(240, 0.04, volume=0.05)))
    if sound_id == "steel_hit":
        return _make_sound(_append(_tone(1180, 0.04, volume=0.16), _tone(860, 0.045, volume=0.1)))
    if sound_id == "player_hit":
        return _make_sound(_append(_noise(0.075, volume=0.1, lowpass=0.28), _tone(180, 0.08, volume=0.1)))
    if sound_id == "enemy_destroyed":
        return _make_sound(_append(_noise(0.085, volume=0.1, lowpass=0.28), _tone(145, 0.08, volume=0.08)))
    if sound_id == "eagle_destroyed":
        return _make_sound(_append(_noise(0.14, volume=0.12, lowpass=0.22), _tone(90, 0.18, volume=0.12)))
    if sound_id == "victory":
        return _make_sound(
            _append(
                _tone(392, 0.09, volume=0.14),
                _tone(523, 0.09, volume=0.14),
                _tone(659, 0.12, volume=0.15),
                _tone(784, 0.18, volume=0.16),
            )
        )
    if sound_id == "defeat":
        return _make_sound(
            _append(
                _tone(330, 0.08, volume=0.12),
                _tone(247, 0.1, volume=0.12),
                _tone(175, 0.16, volume=0.12),
                _tone(131, 0.2, volume=0.1),
            )
        )
    return _make_sound(_tone(440, 0.08, volume=0.15))


def generate_ambience(ambience_id: str) -> pygame.mixer.Sound:
    if ambience_id == "menu_battlefield":
        bed = _tone(52, 3.2, volume=0.03, waveform="triangle", attack=0.18, decay=0.35)
        distant = _append(
            _silence(0.7),
            _noise(0.07, volume=0.02, lowpass=0.93),
            _silence(0.8),
            _noise(0.05, volume=0.018, lowpass=0.9),
            _silence(1.58),
        )
        return _make_sound(_mix(bed, distant))
    if ambience_id == "menu_radio":
        return _make_sound(_append(_silence(1.2), _tone(980, 0.03, volume=0.015, waveform="square"), _silence(1.2)))
    if ambience_id == "gameplay_rumble":
        low = _tone(64, 2.2, volume=0.028, waveform="triangle", attack=0.1, decay=0.2)
        thump = _append(
            _silence(0.32),
            _tone(96, 0.035, volume=0.02, waveform="square"),
            _silence(0.56),
            _tone(92, 0.03, volume=0.018, waveform="square"),
            _silence(1.255),
        )
        return _make_sound(_mix(low, thump))
    if ambience_id == "boss_tension":
        drone = _tone(82, 2.8, volume=0.035, waveform="triangle", attack=0.12, decay=0.2)
        alert = _append(
            _silence(0.48),
            _tone(220, 0.06, volume=0.018, waveform="square"),
            _silence(0.22),
            _tone(196, 0.06, volume=0.016, waveform="square"),
            _silence(1.98),
        )
        return _make_sound(_mix(drone, alert))
    return _make_sound(_noise(1.5, volume=0.04))


def generate_music(track_id: str) -> pygame.mixer.Sound:
    if track_id == "menu_theme":
        return _make_sound(
            _append(
                _mix(_tone(220, 0.22, volume=0.06), _tone(330, 0.22, volume=0.035)),
                _mix(_tone(247, 0.22, volume=0.06), _tone(370, 0.22, volume=0.03)),
                _mix(_tone(294, 0.22, volume=0.06), _tone(440, 0.22, volume=0.03)),
                _mix(_tone(262, 0.22, volume=0.06), _tone(392, 0.22, volume=0.03)),
                _mix(_tone(220, 0.28, volume=0.06), _tone(330, 0.28, volume=0.03)),
            )
        )
    if track_id == "gameplay_theme":
        bass = _append(
            _pulse(146, 0.1, volume=0.07),
            _pulse(146, 0.1, volume=0.07),
            _pulse(174, 0.1, volume=0.07),
            _pulse(196, 0.12, volume=0.07),
        )
        lead = _append(
            _silence(0.06),
            _tone(440, 0.1, volume=0.028),
            _tone(392, 0.1, volume=0.028),
            _tone(349, 0.12, volume=0.028),
            _tone(392, 0.1, volume=0.026),
        )
        return _make_sound(_mix(bass, lead))
    if track_id == "boss_theme":
        march = _append(
            _pulse(98, 0.11, volume=0.08),
            _pulse(98, 0.11, volume=0.08),
            _pulse(110, 0.11, volume=0.08),
            _pulse(98, 0.11, volume=0.08),
            _pulse(82, 0.14, volume=0.08),
        )
        brass = _append(
            _silence(0.05),
            _tone(196, 0.11, volume=0.03, waveform="triangle"),
            _tone(220, 0.11, volume=0.03, waveform="triangle"),
            _tone(196, 0.11, volume=0.03, waveform="triangle"),
            _tone(165, 0.14, volume=0.03, waveform="triangle"),
            _silence(0.05),
        )
        return _make_sound(_mix(march, brass))
    if track_id == "victory_theme":
        return _make_sound(
            _append(
                _mix(_tone(392, 0.12, volume=0.08), _tone(523, 0.12, volume=0.04)),
                _mix(_tone(494, 0.12, volume=0.08), _tone(659, 0.12, volume=0.04)),
                _mix(_tone(587, 0.16, volume=0.09), _tone(784, 0.16, volume=0.045)),
                _mix(_tone(784, 0.26, volume=0.1), _tone(1046, 0.26, volume=0.05)),
            )
        )
    if track_id == "defeat_theme":
        return _make_sound(
            _append(
                _mix(_tone(262, 0.14, volume=0.07), _tone(196, 0.14, volume=0.03)),
                _mix(_tone(220, 0.16, volume=0.07), _tone(165, 0.16, volume=0.03)),
                _mix(_tone(175, 0.22, volume=0.08), _tone(131, 0.22, volume=0.035)),
                _silence(0.06),
            )
        )
    return _make_sound(_tone(220, 0.2, volume=0.08))
