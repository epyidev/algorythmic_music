"""
Filtres résonants, en passe-bas, passe-haut et passe-bande.

La résonance est obtenue en montant l'ordre du filtre autour de la coupure
plutôt qu'en bouclant un gain : le résultat reste stable quelle que soit la
valeur choisie.

@author epyidev
"""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, sosfilt

from ..parameters import Parameter

MIN_CUTOFF_HZ = 40.0
MAX_CUTOFF_HZ = 16000.0
DEFAULT_LOW_CUTOFF = 2000.0
DEFAULT_HIGH_CUTOFF = 200.0
DEFAULT_BAND_CUTOFF = 900.0
NYQUIST_RATIO = 0.48
BAND_WIDTH_FLOOR = 1.1
MIN_ORDER = 2
MAX_ORDER = 8

CUTOFF = Parameter("cutoff", "Coupure", MIN_CUTOFF_HZ, MAX_CUTOFF_HZ,
                   DEFAULT_LOW_CUTOFF, " Hz", decimals=0)
RESONANCE = Parameter("resonance", "Résonance", 0.0, 1.0, 0.0)
WIDTH = Parameter("width", "Largeur", 1.2, 6.0, 2.0)


def _order(values: dict[str, float]) -> int:
    """Traduit la résonance en ordre de filtre."""
    return int(MIN_ORDER + (MAX_ORDER - MIN_ORDER) * values["resonance"])


def _bounded(cutoff: float, sample_rate: int) -> float:
    return min(max(cutoff, MIN_CUTOFF_HZ), sample_rate * NYQUIST_RATIO)


def lowpass(signal: np.ndarray, sample_rate: int, values: dict[str, float]) -> np.ndarray:
    """Coupe au-dessus de la fréquence choisie."""
    cutoff = _bounded(values["cutoff"], sample_rate)
    sections = butter(_order(values), cutoff, btype="low", fs=sample_rate, output="sos")
    return sosfilt(sections, signal)


def highpass(signal: np.ndarray, sample_rate: int, values: dict[str, float]) -> np.ndarray:
    """Coupe en dessous de la fréquence choisie."""
    cutoff = _bounded(values["cutoff"], sample_rate)
    sections = butter(_order(values), cutoff, btype="high", fs=sample_rate, output="sos")
    return sosfilt(sections, signal)


def bandpass(signal: np.ndarray, sample_rate: int, values: dict[str, float]) -> np.ndarray:
    """Ne laisse passer qu'une bande autour de la fréquence choisie."""
    centre = _bounded(values["cutoff"], sample_rate)
    width = max(values["width"], BAND_WIDTH_FLOOR)
    low = _bounded(centre / width, sample_rate)
    high = _bounded(centre * width, sample_rate)
    if high <= low * BAND_WIDTH_FLOOR:
        return signal
    sections = butter(
        _order(values), (low, high), btype="band", fs=sample_rate, output="sos"
    )
    return sosfilt(sections, signal)
