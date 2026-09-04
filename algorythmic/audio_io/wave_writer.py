"""
Écriture d'un mixage stéréo en WAV entier signé.

@author epyidev
"""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

from ..config.audio_format import CHANNEL_COUNT, SAMPLE_WIDTH_BYTES
from .pcm import to_int16


def write_wave(path: Path, stereo: np.ndarray, sample_rate: int) -> None:
    """Écrit le mixage à l'emplacement demandé, en créant le dossier au besoin."""
    path = Path(path)
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)

    frames = to_int16(stereo)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(CHANNEL_COUNT)
        handle.setsampwidth(SAMPLE_WIDTH_BYTES)
        handle.setframerate(sample_rate)
        handle.writeframes(frames.tobytes())
