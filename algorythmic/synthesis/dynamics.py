"""
Dynamique de sortie : compression douce, saturation, normalisation, fondus.

Le facteur de crête visé est d'environ treize décibels, soit celui d'un
mixage acoustique et non celui d'une production compressée.

@author epyidev
"""

from __future__ import annotations

import numpy as np
from scipy.signal import oaconvolve

DETECTOR_SECONDS = 0.06
THRESHOLD = 0.09
COMPRESSION_RATIO = 0.18
SATURATION_DRIVE = 2.4
OUTPUT_PEAK = 0.89
EDGE_FADE_SECONDS = 0.05
LEVEL_GUARD = 1e-9


def normalise(stereo: np.ndarray, peak: float = 1.0) -> np.ndarray:
    """Ramène le plus fort échantillon au niveau demandé."""
    return stereo * (peak / (np.max(np.abs(stereo)) + LEVEL_GUARD))


def compress(stereo: np.ndarray, sample_rate: int) -> np.ndarray:
    """Compresse au-dessus du seuil, avec un détecteur lissé donc sans pompage."""
    detector = np.maximum(np.abs(stereo[0]), np.abs(stereo[1]))
    window = np.hanning(int(DETECTOR_SECONDS * sample_rate))
    window /= window.sum()
    detector = oaconvolve(detector, window, mode="same")

    reduction = np.where(
        detector > THRESHOLD,
        (THRESHOLD + (detector - THRESHOLD) * COMPRESSION_RATIO)
        / (detector + LEVEL_GUARD),
        1.0,
    )
    return stereo * reduction


def saturate(stereo: np.ndarray) -> np.ndarray:
    """Arrondit les crêtes restantes plutôt que de les écrêter."""
    return np.tanh(stereo * SATURATION_DRIVE) / np.tanh(SATURATION_DRIVE)


def apply_edge_fades(stereo: np.ndarray, sample_rate: int) -> np.ndarray:
    """Ouvre et ferme le fichier sur un fondu court, pour éviter tout clic."""
    fade_samples = int(EDGE_FADE_SECONDS * sample_rate)
    if fade_samples * 2 >= stereo.shape[1]:
        return stereo
    stereo[:, :fade_samples] *= np.linspace(0.0, 1.0, fade_samples)
    stereo[:, -fade_samples:] *= np.linspace(1.0, 0.0, fade_samples)
    return stereo


def finalise(stereo: np.ndarray, sample_rate: int) -> np.ndarray:
    """Enchaîne compression, saturation, normalisation et fondus."""
    stereo = compress(normalise(stereo), sample_rate)
    stereo = normalise(saturate(stereo), OUTPUT_PEAK)
    return apply_edge_fades(stereo, sample_rate)
