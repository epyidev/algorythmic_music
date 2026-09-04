"""
Conversion d'un mixage flottant en échantillons entiers.

@author epyidev
"""

from __future__ import annotations

import numpy as np

from ..config.audio_format import FULL_SCALE

LITTLE_ENDIAN_INT16 = "<i2"


def to_int16(stereo: np.ndarray) -> np.ndarray:
    """Entrelace les deux canaux et les convertit en entiers seize bits."""
    return (np.clip(stereo.T, -1.0, 1.0) * FULL_SCALE).astype(LITTLE_ENDIAN_INT16)


def to_bytes(stereo: np.ndarray) -> bytes:
    """Rend le mixage sous forme d'octets, prêts à être joués ou écrits."""
    return to_int16(stereo).tobytes()
