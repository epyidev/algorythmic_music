"""
Réverbération par convolution avec une réponse impulsionnelle synthétique.

Les deux canaux sont décorrélés : la queue élargit l'image sans déplacer la
source, ce qui laisse le mixage mono compatible.

@author epyidev
"""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, oaconvolve, sosfilt

STEREO_CHANNELS = 2
DECAY_TIME = 1.5
TAIL_LENGTH = 3.2
DAMPING_HZ = 2400.0
DAMPING_ORDER = 2
PRE_DELAY = 0.012
NORMALISE_GUARD = 1e-9


def build_impulse_response(rng: np.random.Generator, sample_rate: int) -> np.ndarray:
    """Construit une queue de réverbération stéréo, un canal par ligne."""
    sample_count = int(TAIL_LENGTH * sample_rate)
    time = np.arange(sample_count) / sample_rate
    sections = butter(
        DAMPING_ORDER, DAMPING_HZ, btype="low", fs=sample_rate, output="sos"
    )
    pre_delay_samples = int(PRE_DELAY * sample_rate)

    channels = []
    for _ in range(STEREO_CHANNELS):
        tail = rng.normal(0.0, 1.0, sample_count) * np.exp(-time / DECAY_TIME)
        tail = sosfilt(sections, tail)
        tail[:pre_delay_samples] = 0.0
        channels.append(tail / (np.max(np.abs(tail)) + NORMALISE_GUARD))
    return np.array(channels)


def convolve_tail(signal: np.ndarray, tail: np.ndarray) -> np.ndarray:
    """Applique une queue de réverbération et tronque à la longueur d'entrée."""
    wet = oaconvolve(signal, tail)[: len(signal)]
    return wet / (np.max(np.abs(wet)) + NORMALISE_GUARD)
