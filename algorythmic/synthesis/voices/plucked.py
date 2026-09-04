"""
Voix de corde pincée, par guide d'onde de Karplus et Strong.

Un court bruit est injecté dans une ligne à retard bouclée sur elle-même à
la période de la note. Le filtre moyenneur du retour mange les aigus à
chaque tour, ce qui produit l'extinction naturelle d'une corde.

La boucle est écrite comme un filtre récursif : la calculer échantillon par
échantillon en Python coûterait plusieurs secondes par note.

@author epyidev
"""

from __future__ import annotations

import numpy as np
from scipy.signal import lfilter

from ...config.layer_settings import Timbre
from ...model.scale import midi_to_frequency
from .spec import VoiceSpec

MIN_DAMPING = 0.960
MAX_DAMPING = 0.999
MIN_PERIOD_SAMPLES = 2
EXCITATION_PERIODS = 1.0
BRIGHTNESS_TILT = 0.7


def render(
    midi: int,
    duration: float,
    rng: np.random.Generator,
    spec: VoiceSpec,
    timbre: Timbre,
    sample_rate: int,
) -> np.ndarray:
    """Excite une ligne à retard bouclée et rend son extinction."""
    sample_count = int(duration * sample_rate)
    fundamental = midi_to_frequency(midi) * (
        1.0 + rng.normal(0.0, spec.detune * timbre.detune)
    )
    period = max(int(sample_rate / fundamental), MIN_PERIOD_SAMPLES)

    excitation = np.zeros(sample_count)
    burst_length = min(int(period * EXCITATION_PERIODS), sample_count)
    burst = rng.normal(0.0, 1.0, burst_length)
    # La brillance dose la part d'aigus présente dans l'excitation de départ.
    burst = burst * timbre.brightness + np.cumsum(burst) / burst_length * (
        1.0 - timbre.brightness * BRIGHTNESS_TILT
    )
    excitation[:burst_length] = burst

    # Le caractère règle la longueur d'extinction, du pizzicato sec au son tenu.
    damping = MIN_DAMPING + (MAX_DAMPING - MIN_DAMPING) * timbre.character
    feedback = np.zeros(period + 2)
    feedback[0] = 1.0
    feedback[period] = -damping / 2.0
    feedback[period + 1] = -damping / 2.0

    signal = lfilter([1.0], feedback, excitation)
    return signal / (np.max(np.abs(signal)) + 1e-12)
