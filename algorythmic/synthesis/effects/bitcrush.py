"""
Réduction de définition : moins de bits, moins d'échantillons par seconde.

C'est le seul effet du lot qui salit volontairement le signal. Le repliement
qu'il produit fait partie du résultat recherché.

@author epyidev
"""

from __future__ import annotations

import numpy as np

from ..parameters import Parameter

BITS = Parameter("bits", "Définition", 2.0, 16.0, 6.0, " bits", decimals=0)
DOWNSAMPLE = Parameter("downsample", "Décimation", 1.0, 48.0, 8.0, "x", decimals=0)
MIX = Parameter("mix", "Mélange", 0.0, 1.0, 1.0)
LEVEL_GUARD = 1e-12


def crush(signal: np.ndarray, sample_rate: int, values: dict[str, float]) -> np.ndarray:
    """Quantifie l'amplitude, puis tient chaque échantillon plusieurs fois."""
    peak = float(np.max(np.abs(signal))) + LEVEL_GUARD
    scaled = signal / peak

    levels = 2.0 ** int(values["bits"]) / 2.0
    quantised = np.round(scaled * levels) / levels

    factor = max(int(values["downsample"]), 1)
    if factor > 1:
        held = np.repeat(quantised[::factor], factor)[: len(signal)]
        quantised = np.pad(held, (0, len(signal) - len(held)))

    crushed = quantised * peak
    return signal * (1.0 - values["mix"]) + crushed * values["mix"]
