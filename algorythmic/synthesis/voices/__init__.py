"""
Les timbres disponibles, et le rendu d'une note quel que soit le timbre.

L'enveloppe est appliquée ici, une fois pour toutes : c'est elle qui garantit
qu'une note commence et finit à zéro, donc qu'aucun dépôt dans le tampon ne
produit de clic.

@author epyidev
"""

from __future__ import annotations

import numpy as np

from ...config.layer_settings import Timbre
from ..envelope import adsr
from . import additive, fm, plucked, pulse
from .spec import VoiceSpec

VOICE_RENDERERS = {
    "additive": additive.render,
    "fm": fm.render,
    "pulse": pulse.render,
    "plucked": plucked.render,
}

VOICE_LABELS: dict[str, str] = {
    "additive": "Additif (nappe)",
    "fm": "Modulation de fréquence",
    "pulse": "Impulsion filtrée",
    "plucked": "Corde pincée",
}

MIN_ATTACK = 0.004
NORMALISE_GUARD = 1e-12

__all__ = ["VOICE_LABELS", "VOICE_RENDERERS", "VoiceSpec", "render_voice"]


def render_voice(
    midi: int,
    duration: float,
    rng: np.random.Generator,
    spec: VoiceSpec,
    sample_rate: int,
    timbre: Timbre,
) -> np.ndarray:
    """Synthétise une note avec le timbre demandé, enveloppe comprise."""
    sample_count = int(duration * sample_rate)
    if sample_count <= 0:
        return np.zeros(0)

    renderer = VOICE_RENDERERS.get(timbre.kind, additive.render)
    signal = renderer(midi, duration, rng, spec, timbre, sample_rate)

    attack = max(spec.attack * timbre.attack, MIN_ATTACK)
    release = min(duration * spec.release_ratio, spec.max_release)
    signal = signal * adsr(
        sample_count, attack, spec.decay, spec.sustain, release, sample_rate
    )
    return signal / (np.max(np.abs(signal)) + NORMALISE_GUARD)
