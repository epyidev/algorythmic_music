"""
Voix additive.

Les partiels décroissent en puissance inverse de leur rang, ce qui donne un
timbre déjà sombre avant même le filtrage global. Chaque partiel est
légèrement désaccordé et vibre sous le seuil de perception consciente : c'est
ce flottement qui empêche le son de paraître synthétique.

@author epyidev
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..model.scale import midi_to_frequency
from .envelope import adsr

FIRST_PARTIAL = 1
FULL_TURN = 2.0 * np.pi


@dataclass(frozen=True)
class VoiceSpec:
    """Réglages d'un timbre, indépendants de la hauteur et de la durée."""

    partial_count: int
    decay_exponent: float
    attack: float
    detune: float = 0.0025
    decay: float = 0.12
    sustain: float = 0.55
    vibrato_depth: float = 0.0015
    vibrato_lowest_hz: float = 0.3
    vibrato_highest_hz: float = 0.8
    release_ratio: float = 0.6
    max_release: float = 1.1


def render_voice(
    midi: int,
    duration: float,
    rng: np.random.Generator,
    spec: VoiceSpec,
    sample_rate: int,
) -> np.ndarray:
    """Synthétise une note et rend son signal mono normalisé."""
    sample_count = int(duration * sample_rate)
    if sample_count <= 0:
        return np.zeros(0)

    time = np.arange(sample_count) / sample_rate
    fundamental = midi_to_frequency(midi)
    signal = np.zeros(sample_count)

    for rank in range(FIRST_PARTIAL, spec.partial_count + 1):
        amplitude = 1.0 / (rank ** spec.decay_exponent)
        drift = 1.0 + rng.normal(0.0, spec.detune)
        phase = rng.uniform(0.0, FULL_TURN)
        vibrato_rate = rng.uniform(spec.vibrato_lowest_hz, spec.vibrato_highest_hz)
        vibrato = 1.0 + spec.vibrato_depth * np.sin(FULL_TURN * vibrato_rate * time + phase)
        signal += amplitude * np.sin(
            FULL_TURN * fundamental * rank * drift * vibrato * time + phase
        )

    release = min(duration * spec.release_ratio, spec.max_release)
    signal *= adsr(
        sample_count, spec.attack, spec.decay, spec.sustain, release, sample_rate
    )

    total_amplitude = sum(
        1.0 / rank ** spec.decay_exponent
        for rank in range(FIRST_PARTIAL, spec.partial_count + 1)
    )
    return signal / total_amplitude
