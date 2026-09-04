"""
Dépôt d'un signal dans un tampon, à un instant donné.

@author epyidev
"""

from __future__ import annotations

import numpy as np


def place_signal(
    buffer: np.ndarray, signal: np.ndarray, start_time: float, sample_rate: int
) -> None:
    """Ajoute un signal au tampon, en tronquant ce qui déborde des deux bords."""
    start = int(start_time * sample_rate)
    if start < 0:
        signal = signal[-start:]
        start = 0
    end = min(start + len(signal), len(buffer))
    if end > start:
        buffer[start:end] += signal[: end - start]
