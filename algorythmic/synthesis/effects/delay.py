"""
Écho à réinjection.

Les répétitions sont sommées une par une jusqu'à devenir inaudibles. Écrire
la boucle de retour comme un filtre récursif serait plus court, mais son
ordre vaudrait la longueur du retard, soit des dizaines de milliers de
coefficients à appliquer à chaque échantillon.

@author epyidev
"""

from __future__ import annotations

import numpy as np

from ..parameters import Parameter

MILLISECONDS = 1000.0
MAX_FEEDBACK = 0.92
MIN_DELAY_SAMPLES = 1
INAUDIBLE_GAIN = 1e-4

TIME = Parameter("time", "Retard", 10.0, 1500.0, 340.0, " ms", decimals=0)
FEEDBACK = Parameter("feedback", "Réinjection", 0.0, MAX_FEEDBACK, 0.35)
MIX = Parameter("mix", "Mélange", 0.0, 1.0, 0.35)


def echo(signal: np.ndarray, sample_rate: int, values: dict[str, float]) -> np.ndarray:
    """Répète le signal à intervalle fixe, chaque répétition plus faible."""
    delay_samples = max(
        int(values["time"] / MILLISECONDS * sample_rate), MIN_DELAY_SAMPLES
    )
    if delay_samples >= len(signal):
        return signal

    feedback = min(values["feedback"], MAX_FEEDBACK)
    wet = np.zeros_like(signal)
    gain = 1.0
    shift = delay_samples

    while gain > INAUDIBLE_GAIN and shift < len(signal):
        wet[shift:] += signal[: len(signal) - shift] * gain
        gain *= feedback
        shift += delay_samples

    return signal * (1.0 - values["mix"]) + wet * values["mix"]
