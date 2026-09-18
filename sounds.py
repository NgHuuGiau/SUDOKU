"""Sound manager for Sudoku game - generates simple tones programmatically."""

import array
import math

import pygame

from error_handling import logger
from persistence import get_preference, set_preference


def generate_tone(
    frequency: float,
    duration: float,
    volume: float = 0.5,
    sample_rate: int = 44100,
) -> pygame.mixer.Sound:
    """Generate a simple sine wave tone."""
    sample_rate = 44100 if sample_rate is None else sample_rate
    n_samples = int(sample_rate * duration)
    buf = array.array("h", [0] * n_samples)
    amplitude = int(32767 * volume)

    for i in range(n_samples):
        t = i / sample_rate
        envelope = 1.0
        if i < n_samples * 0.1:
            envelope = i / (n_samples * 0.1)
        elif i > n_samples * 0.8:
            envelope = (n_samples - i) / (n_samples * 0.2)
        buf[i] = int(amplitude * envelope * math.sin(2 * math.pi * frequency * t))

    sound = pygame.mixer.Sound(buffer=buf)
    return sound


def generate_click(volume: float = 0.3) -> pygame.mixer.Sound:
    """Generate a short click sound."""
    return generate_tone(800, 0.05, volume)


def generate_pop(volume: float = 0.4) -> pygame.mixer.Sound:
    """Generate a pop sound for number entry."""
    return generate_tone(600, 0.08, volume)


def generate_success(volume: float = 0.5) -> pygame.mixer.Sound:
    """Generate a success chime (ascending tones)."""
    sample_rate = 44100
    duration = 0.5
    n_samples = int(sample_rate * duration)
    buf = array.array("h", [0] * n_samples)
    amplitude = int(32767 * volume)

    for i in range(n_samples):
        t = i / sample_rate
        # Ascending chord: C5, E5, G5
        freq1 = 523.25  # C5
        freq2 = 659.25  # E5
        freq3 = 783.99  # G5
        envelope = 1.0
        if i < n_samples * 0.1:
            envelope = i / (n_samples * 0.1)
        elif i > n_samples * 0.7:
            envelope = (n_samples - i) / (n_samples * 0.3)
        val = (
            math.sin(2 * math.pi * freq1 * t)
            + math.sin(2 * math.pi * freq2 * t)
            + math.sin(2 * math.pi * freq3 * t)
        ) / 3
        buf[i] = int(amplitude * envelope * val)

    sound = pygame.mixer.Sound(buffer=buf)
    return sound


def generate_hint(volume: float = 0.4) -> pygame.mixer.Sound:
    """Generate a hint sound (gentle chime)."""
    sample_rate = 44100
    duration = 0.3
    n_samples = int(sample_rate * duration)
    buf = array.array("h", [0] * n_samples)
    amplitude = int(32767 * volume)

    for i in range(n_samples):
        t = i / sample_rate
        # Gentle E6
        freq = 1318.51
        envelope = 1.0
        if i < n_samples * 0.05:
            envelope = i / (n_samples * 0.05)
        elif i > n_samples * 0.6:
            envelope = (n_samples - i) / (n_samples * 0.4)
        buf[i] = int(amplitude * envelope * math.sin(2 * math.pi * freq * t))

    sound = pygame.mixer.Sound(buffer=buf)
    return sound


def generate_undo(volume: float = 0.3) -> pygame.mixer.Sound:
    """Generate an undo sound (soft reverse)."""
    sample_rate = 44100
    duration = 0.15
    n_samples = int(sample_rate * duration)
    buf = array.array("h", [0] * n_samples)
    amplitude = int(32767 * volume)

    for i in range(n_samples):
        t = i / sample_rate
        # Descending tone
        freq = 800 - 400 * t / duration
        envelope = 1.0
        if i < n_samples * 0.1:
            envelope = i / (n_samples * 0.1)
        elif i > n_samples * 0.7:
            envelope = (n_samples - i) / (n_samples * 0.3)
        buf[i] = int(amplitude * envelope * math.sin(2 * math.pi * freq * t))

    sound = pygame.mixer.Sound(buffer=buf)
    return sound


class SoundManager:
    """Manages all game sound effects."""

    def __init__(self):
        self.sounds = {}
        enabled = get_preference("sound_enabled", True)
        self.enabled = enabled if type(enabled) is bool else True
        self._init_sounds()

    def _init_sounds(self):
        """Initialize all sound effects."""
        try:
            self.sounds = {
                "click": generate_click(),
                "pop": generate_pop(),
                "success": generate_success(),
                "hint": generate_hint(),
                "undo": generate_undo(),
            }
        except pygame.error as exc:
            logger.warning("Could not initialize sound effects: %s", exc)
            self.sounds = {}

    def play(self, name: str):
        """Play a sound by name."""
        if not self.enabled or name not in self.sounds:
            return
        try:
            self.sounds[name].play()
        except pygame.error as exc:
            self.sounds.pop(name, None)
            logger.warning("Disabling unavailable sound effect %s: %s", name, exc)

    def toggle(self):
        """Toggle sound on/off."""
        self.enabled = not self.enabled
        set_preference("sound_enabled", self.enabled)

    def is_enabled(self) -> bool:
        return self.enabled


# Global sound manager instance
_sound_manager = None


def get_sound_manager() -> SoundManager:
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager


def play_sound(name: str):
    """Convenience function to play a sound."""
    get_sound_manager().play(name)


def toggle_sound():
    get_sound_manager().toggle()


def is_sound_enabled() -> bool:
    return get_sound_manager().is_enabled()
