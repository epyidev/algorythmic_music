"""
Enveloppes d'amplitude.

Aucune attaque ne descend sous vingt millisecondes : c'est ce qui rend la
pulsation floue au lieu de percussive.

@author epyidev
"""

from __future__ import annotations

import numpy as np

ATTACK_CURVE_EXPONENT = 1.6
RELEASE_CURVE_EXPONENT = 1.8
MIN_SEGMENT_SAMPLES = 1


def adsr(
    sample_count: int,
    attack: float,
    decay: float,
    sustain: float,
    release: float,
    sample_rate: int,
) -> np.ndarray:
    """Construit une enveloppe attaque, chute, tenue, extinction."""
    if sample_count <= 0:
        return np.zeros(0)

    attack_samples = max(int(attack * sample_rate), MIN_SEGMENT_SAMPLES)
    decay_samples = max(int(decay * sample_rate), MIN_SEGMENT_SAMPLES)
    release_samples = max(int(release * sample_rate), MIN_SEGMENT_SAMPLES)
    sustain_samples = max(
        sample_count - attack_samples - decay_samples - release_samples, 0
    )

    curve = np.concatenate([
        np.linspace(0.0, 1.0, attack_samples) ** ATTACK_CURVE_EXPONENT,
        np.linspace(1.0, sustain, decay_samples),
        np.full(sustain_samples, sustain),
        np.linspace(sustain, 0.0, release_samples) ** RELEASE_CURVE_EXPONENT,
    ])

    if len(curve) >= sample_count:
        return curve[:sample_count]
    return np.pad(curve, (0, sample_count - len(curve)))
