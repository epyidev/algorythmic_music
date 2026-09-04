"""
Voix par modulation de fréquence, deux opérateurs.

Un seul modulateur suffit à sortir du registre des sons doux : selon le
rapport de fréquence, le résultat va de la cloche métallique au timbre de
cuivre. L'indice de modulation décroît pendant la note, comme sur un
instrument réel dont l'attaque est plus riche que la tenue.

@author epyidev
"""

from __future__ import annotations

import numpy as np

from ...config.layer_settings import Timbre
from ...model.scale import midi_to_frequency
from .spec import VoiceSpec, vibrato_excursion

FULL_TURN = 2.0 * np.pi
MAX_INDEX = 8.0
INDEX_DECAY = 2.6
RATIO_CHOICES = (0.5, 1.0, 1.5, 2.0, 3.0, 3.5, 5.0, 7.0)


def render(
    midi: int,
    duration: float,
    rng: np.random.Generator,
    spec: VoiceSpec,
    timbre: Timbre,
    sample_rate: int,
) -> np.ndarray:
    """Module la fréquence d'une porteuse par un oscillateur harmonique."""
    sample_count = int(duration * sample_rate)
    time = np.arange(sample_count) / sample_rate
    carrier = midi_to_frequency(midi) * (
        1.0 + rng.normal(0.0, spec.detune * timbre.detune)
    )

    # Le caractère choisit le rapport porteuse sur modulateur.
    ratio_index = int(timbre.character * (len(RATIO_CHOICES) - 1) + 0.5)
    ratio = RATIO_CHOICES[ratio_index]

    index = MAX_INDEX * timbre.brightness * np.exp(-time * INDEX_DECAY)
    modulator = np.sin(FULL_TURN * carrier * ratio * time)

    offset = rng.uniform(0.0, FULL_TURN)
    excursion = time + vibrato_excursion(
        time,
        spec.vibrato_depth,
        rng.uniform(spec.vibrato_lowest_hz, spec.vibrato_highest_hz),
        offset,
    )
    return np.sin(FULL_TURN * carrier * excursion + offset + index * modulator)
