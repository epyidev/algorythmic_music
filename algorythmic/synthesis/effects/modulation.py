"""
Effets qui font varier le signal dans le temps : chorus, trémolo, modulation
en anneau.

@author epyidev
"""

from __future__ import annotations

import numpy as np

from ..parameters import Parameter

FULL_TURN = 2.0 * np.pi
MILLISECONDS = 1000.0

CHORUS_RATE = Parameter("rate", "Vitesse", 0.05, 8.0, 0.6, " Hz")
CHORUS_DEPTH = Parameter("depth", "Profondeur", 0.5, 25.0, 6.0, " ms")
CHORUS_MIX = Parameter("mix", "Mélange", 0.0, 1.0, 0.5)

TREMOLO_RATE = Parameter("rate", "Vitesse", 0.1, 24.0, 4.0, " Hz")
TREMOLO_DEPTH = Parameter("depth", "Profondeur", 0.0, 1.0, 0.6)
TREMOLO_SHAPE = Parameter("shape", "Dureté", 1.0, 8.0, 1.0)

RING_FREQUENCY = Parameter("frequency", "Fréquence", 10.0, 3000.0, 220.0, " Hz",
                           decimals=0)
RING_MIX = Parameter("mix", "Mélange", 0.0, 1.0, 0.6)


def chorus(signal: np.ndarray, sample_rate: int, values: dict[str, float]) -> np.ndarray:
    """Superpose une copie dont le retard oscille, ce qui épaissit la note."""
    time = np.arange(len(signal)) / sample_rate
    depth_samples = values["depth"] / MILLISECONDS * sample_rate
    offset = depth_samples * (1.0 + np.sin(FULL_TURN * values["rate"] * time)) / 2.0

    positions = np.arange(len(signal)) - offset
    delayed = np.interp(positions, np.arange(len(signal)), signal, left=0.0)
    return signal * (1.0 - values["mix"]) + delayed * values["mix"]


def tremolo(signal: np.ndarray, sample_rate: int, values: dict[str, float]) -> np.ndarray:
    """Fait battre le volume à vitesse fixe."""
    time = np.arange(len(signal)) / sample_rate
    wave = (1.0 + np.sin(FULL_TURN * values["rate"] * time)) / 2.0
    # La dureté transforme l'ondulation douce en pulsation hachée.
    wave = wave ** values["shape"]
    return signal * (1.0 - values["depth"] + values["depth"] * wave)


def ring_modulator(
    signal: np.ndarray, sample_rate: int, values: dict[str, float]
) -> np.ndarray:
    """Multiplie le signal par une sinusoïde : timbre métallique, inharmonique."""
    time = np.arange(len(signal)) / sample_rate
    carrier = np.sin(FULL_TURN * values["frequency"] * time)
    return signal * (1.0 - values["mix"]) + signal * carrier * values["mix"]
