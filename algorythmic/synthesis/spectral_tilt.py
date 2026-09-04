"""
Basculement spectral : le paramètre le plus important du modèle.

Le mixage est ramené vers une pente d'environ douze décibels par octave entre
cent hertz et un kilohertz, ce qui produit la sensation d'un morceau entendu à
travers une cloison. Deux précautions comptent : le spectre mesuré est lissé
sur une demi-octave, sinon on mesure les creux entre partiels au lieu de
l'enveloppe, et la correction est recentrée sur sa médiane, sinon elle se
réduit à un gain global.

@author epyidev
"""

from __future__ import annotations

import numpy as np
from scipy.signal import oaconvolve

TILT_CURVE = (
    (20.0, -20.0), (50.0, -14.0), (100.0, 0.0), (200.0, -7.0),
    (400.0, -14.0), (800.0, -21.0), (1600.0, -31.0), (3200.0, -37.0),
    (6400.0, -38.0), (11000.0, -42.0), (16000.0, -53.0), (22050.0, -72.0),
)

ANALYSIS_SIZE = 8192
ANALYSIS_HOP_FACTOR = 4
SMOOTHING_RATIO = 1.5
CENTRE_BAND_HZ = (80.0, 9000.0)
MIN_GAIN_DB = -30.0
MAX_GAIN_DB = 22.0
DECIBEL_FACTOR = 20.0
POWER_DECIBEL_FACTOR = 10.0
POWER_GUARD = 1e-20
MIN_FREQUENCY_HZ = 1.0


def _average_power_spectrum(signal: np.ndarray, size: int) -> np.ndarray:
    """Moyenne la puissance spectrale sur des fenêtres régulières du signal."""
    window = np.hanning(size)
    accumulator = np.zeros(size // 2 + 1)
    frame_count = 0
    for start in range(0, max(len(signal) - size, 0), size * ANALYSIS_HOP_FACTOR):
        spectrum = np.fft.rfft(signal[start:start + size] * window)
        accumulator += np.abs(spectrum) ** 2
        frame_count += 1
    return accumulator / max(frame_count, 1)


def _smooth_over_half_octave(power: np.ndarray) -> np.ndarray:
    """Lisse la puissance sur une demi-octave, en index comme en fréquence."""
    cumulative = np.concatenate(([0.0], np.cumsum(power)))
    index = np.arange(len(power))
    lowest = np.ceil(index / SMOOTHING_RATIO).astype(int)
    highest = np.minimum(
        np.floor(index * SMOOTHING_RATIO).astype(int), len(power) - 1
    )
    return (cumulative[highest + 1] - cumulative[lowest]) / (highest - lowest + 1)


def build_tilt_filter(
    signal: np.ndarray, sample_rate: int, strength: float, size: int = ANALYSIS_SIZE
) -> np.ndarray:
    """Construit le noyau à phase linéaire qui impose la pente au signal."""
    frequencies = np.fft.rfftfreq(size, 1.0 / sample_rate)
    curve_frequencies = np.array([point[0] for point in TILT_CURVE])
    curve_gains = np.array([point[1] for point in TILT_CURVE])
    target = np.interp(
        np.log10(np.maximum(frequencies, MIN_FREQUENCY_HZ)),
        np.log10(curve_frequencies),
        curve_gains,
    )

    smoothed = _smooth_over_half_octave(_average_power_spectrum(signal, size))
    measured = POWER_DECIBEL_FACTOR * np.log10(
        smoothed / (smoothed.max() + POWER_GUARD) + POWER_GUARD
    )

    correction = target - measured
    band = (frequencies > CENTRE_BAND_HZ[0]) & (frequencies < CENTRE_BAND_HZ[1])
    correction -= np.median(correction[band])
    correction = np.clip(correction * strength, MIN_GAIN_DB, MAX_GAIN_DB)

    kernel = np.fft.irfft(10.0 ** (correction / DECIBEL_FACTOR), size)
    return np.roll(kernel, size // 2) * np.hanning(size)


def apply_tilt(signal: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Applique le noyau en compensant son retard de groupe."""
    delay = len(kernel) // 2
    return oaconvolve(signal, kernel)[delay:delay + len(signal)]
