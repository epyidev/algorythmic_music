"""
Saturation et distorsion.

Le signal est normalisé avant d'entrer dans la courbe, sinon le résultat
dépendrait du niveau de la couche et non du réglage.

@author epyidev
"""

from __future__ import annotations

import numpy as np

from ..parameters import Parameter

AMOUNT = Parameter("amount", "Gain d'entrée", 1.0, 40.0, 6.0)
BIAS = Parameter("bias", "Asymétrie", 0.0, 0.9, 0.0)
MIX = Parameter("mix", "Mélange", 0.0, 1.0, 1.0)
FOLD_AMOUNT = Parameter("amount", "Repliement", 1.0, 12.0, 3.0)
LEVEL_GUARD = 1e-12


def _normalised(signal: np.ndarray) -> tuple[np.ndarray, float]:
    peak = float(np.max(np.abs(signal))) + LEVEL_GUARD
    return signal / peak, peak


def saturate(signal: np.ndarray, sample_rate: int, values: dict[str, float]) -> np.ndarray:
    """Arrondit les crêtes et enrichit le spectre, sans jamais écrêter."""
    scaled, peak = _normalised(signal)
    amount = values["amount"]
    # L'asymétrie fait apparaître les harmoniques paires, plus chaudes.
    driven = np.tanh(scaled * amount + values["bias"]) - np.tanh(values["bias"])
    driven = driven / (np.max(np.abs(driven)) + LEVEL_GUARD) * peak
    return signal * (1.0 - values["mix"]) + driven * values["mix"]


def wavefold(signal: np.ndarray, sample_rate: int, values: dict[str, float]) -> np.ndarray:
    """Replie le signal sur lui-même : distorsion franchement électronique."""
    scaled, peak = _normalised(signal)
    folded = np.sin(np.pi / 2.0 * scaled * values["amount"])
    folded = folded / (np.max(np.abs(folded)) + LEVEL_GUARD) * peak
    return signal * (1.0 - values["mix"]) + folded * values["mix"]
