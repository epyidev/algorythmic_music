"""
Voix additive : une somme de partiels harmoniques décroissants.

C'est le timbre d'origine du projet. Les partiels décroissent en puissance
inverse de leur rang, ce qui donne un son déjà sombre avant tout filtrage.

@author epyidev
"""

from __future__ import annotations

import numpy as np

from ...config.layer_settings import Timbre
from ...model.scale import midi_to_frequency
from .spec import VoiceSpec, highest_audible_rank, vibrato_excursion

FIRST_PARTIAL = 1
FULL_TURN = 2.0 * np.pi
BRIGHTNESS_RANK_SCALE = 1.6
CHARACTER_ODD_BIAS = 2.0


def render(
    midi: int,
    duration: float,
    rng: np.random.Generator,
    spec: VoiceSpec,
    timbre: Timbre,
    sample_rate: int,
) -> np.ndarray:
    """Somme les partiels d'une note et rend le signal brut, sans enveloppe."""
    sample_count = int(duration * sample_rate)
    time = np.arange(sample_count) / sample_rate
    fundamental = midi_to_frequency(midi)

    wanted = max(1, round(spec.partial_count * (1.0 + BRIGHTNESS_RANK_SCALE
                                                * (timbre.brightness - 1.0))))
    rank_count = highest_audible_rank(fundamental, sample_rate, wanted)

    # Un seul vibrato pour toute la voix : les partiels bougent ensemble.
    excursion = time + vibrato_excursion(
        time,
        spec.vibrato_depth,
        rng.uniform(spec.vibrato_lowest_hz, spec.vibrato_highest_hz),
        rng.uniform(0.0, FULL_TURN),
    )

    signal = np.zeros(sample_count)
    total = 0.0
    for rank in range(FIRST_PARTIAL, rank_count + 1):
        amplitude = 1.0 / (rank ** spec.decay_exponent)
        # Le caractère fait glisser le timbre des partiels pairs vers les impairs.
        if rank % 2 == 0:
            amplitude *= 1.0 - timbre.character
        else:
            amplitude *= 1.0 + timbre.character / CHARACTER_ODD_BIAS

        drift = 1.0 + rng.normal(0.0, spec.detune * timbre.detune)
        offset = rng.uniform(0.0, FULL_TURN)
        signal += amplitude * np.sin(
            FULL_TURN * fundamental * rank * drift * excursion + offset
        )
        total += amplitude

    return signal / max(total, 1e-12)
