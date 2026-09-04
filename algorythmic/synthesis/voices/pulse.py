"""
Voix à onde rectangulaire, construite partiel par partiel.

L'onde est reconstituée par ses harmoniques plutôt que dessinée à la main :
aucune fréquence ne dépasse la bande utile, donc aucun repliement. Le
caractère règle la largeur de l'impulsion, du carré plein au filet étroit,
et la brillance règle un passe-bas résonant appliqué ensuite.

@author epyidev
"""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, sosfilt

from ...config.layer_settings import Timbre
from ...model.scale import midi_to_frequency
from .spec import VoiceSpec, highest_audible_rank, vibrato_excursion

FIRST_PARTIAL = 1
FULL_TURN = 2.0 * np.pi
PARTIAL_TARGET = 18
MIN_WIDTH = 0.06
MAX_WIDTH = 0.5
FILTER_ORDER = 2
MIN_CUTOFF_RATIO = 2.0
MAX_CUTOFF_RATIO = 24.0
MIN_CUTOFF_HZ = 120.0
CUTOFF_CEILING_RATIO = 0.45


def render(
    midi: int,
    duration: float,
    rng: np.random.Generator,
    spec: VoiceSpec,
    timbre: Timbre,
    sample_rate: int,
) -> np.ndarray:
    """Empile les harmoniques d'une impulsion, puis les filtre."""
    sample_count = int(duration * sample_rate)
    time = np.arange(sample_count) / sample_rate
    fundamental = midi_to_frequency(midi) * (
        1.0 + rng.normal(0.0, spec.detune * timbre.detune)
    )

    width = MIN_WIDTH + (MAX_WIDTH - MIN_WIDTH) * timbre.character
    rank_count = highest_audible_rank(fundamental, sample_rate, PARTIAL_TARGET)
    offset = rng.uniform(0.0, FULL_TURN)
    excursion = time + vibrato_excursion(
        time,
        spec.vibrato_depth,
        rng.uniform(spec.vibrato_lowest_hz, spec.vibrato_highest_hz),
        offset,
    )

    signal = np.zeros(sample_count)
    for rank in range(FIRST_PARTIAL, rank_count + 1):
        amplitude = np.sin(np.pi * rank * width) / rank
        signal += amplitude * np.sin(
            FULL_TURN * fundamental * rank * excursion + offset
        )

    ratio = MIN_CUTOFF_RATIO + (MAX_CUTOFF_RATIO - MIN_CUTOFF_RATIO) * timbre.brightness
    cutoff = min(
        max(fundamental * ratio, MIN_CUTOFF_HZ), sample_rate * CUTOFF_CEILING_RATIO
    )
    sections = butter(FILTER_ORDER, cutoff, btype="low", fs=sample_rate, output="sos")
    filtered = sosfilt(sections, signal)
    return filtered / (np.max(np.abs(filtered)) + 1e-12)
