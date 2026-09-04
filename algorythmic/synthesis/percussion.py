"""
Percussions volontairement molles et sourdes.

Elles marquent la pulsation sans jamais la trancher : aucune transitoire
franche, pour rester cohérent avec le flou rythmique du reste.

@author epyidev
"""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, sosfilt

FULL_TURN = 2.0 * np.pi

KICK_START_HZ = 62.0
KICK_END_HZ = 38.0
KICK_PITCH_DECAY = 9.0
KICK_AMPLITUDE_DECAY = 7.0

TICK_AMPLITUDE_DECAY = 22.0
TICK_BAND_HZ = (900.0, 2600.0)
TICK_FILTER_ORDER = 2

PERCUSSION_TRIM = 0.9


def render_kick(duration: float, sample_rate: int) -> np.ndarray:
    """Grosse caisse à hauteur descendante, sans clic d'attaque."""
    sample_count = int(duration * sample_rate)
    if sample_count <= 0:
        return np.zeros(0)

    time = np.arange(sample_count) / sample_rate
    frequency = KICK_START_HZ * np.exp(-time * KICK_PITCH_DECAY) + KICK_END_HZ
    phase = FULL_TURN * np.cumsum(frequency) / sample_rate
    return np.sin(phase) * np.exp(-time * KICK_AMPLITUDE_DECAY) * PERCUSSION_TRIM


def render_tick(
    duration: float, rng: np.random.Generator, sample_rate: int
) -> np.ndarray:
    """Bruit filtré très court, qui tient lieu de contretemps."""
    sample_count = int(duration * sample_rate)
    if sample_count <= 0:
        return np.zeros(0)

    time = np.arange(sample_count) / sample_rate
    noise = rng.normal(0.0, 1.0, sample_count) * np.exp(-time * TICK_AMPLITUDE_DECAY)
    sections = butter(
        TICK_FILTER_ORDER, TICK_BAND_HZ, btype="band", fs=sample_rate, output="sos"
    )
    return sosfilt(sections, noise) * PERCUSSION_TRIM
