"""
Réglage de la largeur stéréo par recalage du rapport côté sur milieu.

La cible est atteinte bloc par bloc puis lissée, sinon l'image saute
audiblement à chaque frontière de section.

@author epyidev
"""

from __future__ import annotations

import numpy as np
from scipy.signal import oaconvolve

BLOCK_SECONDS = 1.0
SMOOTHING_SECONDS = 0.5
MAX_WIDTH_FACTOR = 25.0
ENERGY_GUARD = 1e-12


def apply_width(
    left: np.ndarray,
    right: np.ndarray,
    target_width: np.ndarray,
    sample_rate: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Ramène la largeur de l'image sur la cible donnée par l'automation."""
    middle = (left + right) / 2.0
    side = (left - right) / 2.0

    block_size = int(BLOCK_SECONDS * sample_rate)
    factor = np.ones(len(middle))
    for start in range(0, len(middle), block_size):
        end = min(start + block_size, len(middle))
        middle_energy = np.sum(middle[start:end] ** 2) + ENERGY_GUARD
        side_energy = np.sum(side[start:end] ** 2) + ENERGY_GUARD
        wanted = float(np.mean(target_width[start:end]))
        factor[start:end] = np.clip(
            np.sqrt(wanted * middle_energy / side_energy), 0.0, MAX_WIDTH_FACTOR
        )

    smoothing = np.hanning(int(SMOOTHING_SECONDS * sample_rate))
    smoothing /= smoothing.sum()
    factor = oaconvolve(factor, smoothing, mode="same")

    side = side * factor
    return middle + side, middle - side
