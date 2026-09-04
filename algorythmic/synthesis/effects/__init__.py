"""
Catalogue des effets et application d'une chaîne.

Un effet se déclare ici avec son nom affiché, ses réglages et la fonction qui
le calcule. Toute la traversée de l'application, de la fenêtre au moteur, se
fait ensuite sans jamais nommer un effet en particulier.

@author epyidev
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from ...config.layer_settings import EffectSetting
from ..parameters import Parameter, default_values, resolve
from . import bitcrush, delay, drive, filters, modulation


@dataclass(frozen=True)
class EffectKind:
    """Un effet disponible, décrit de façon exploitable par l'interface."""

    key: str
    label: str
    parameters: tuple[Parameter, ...]
    process: Callable[[np.ndarray, int, dict[str, float]], np.ndarray]


EFFECT_KINDS: tuple[EffectKind, ...] = (
    EffectKind("lowpass", "Filtre passe-bas",
               (filters.CUTOFF, filters.RESONANCE), filters.lowpass),
    EffectKind("highpass", "Filtre passe-haut",
               (filters.CUTOFF, filters.RESONANCE), filters.highpass),
    EffectKind("bandpass", "Filtre passe-bande",
               (filters.CUTOFF, filters.WIDTH, filters.RESONANCE), filters.bandpass),
    EffectKind("saturate", "Saturation",
               (drive.AMOUNT, drive.BIAS, drive.MIX), drive.saturate),
    EffectKind("wavefold", "Repliement d'onde",
               (drive.FOLD_AMOUNT, drive.MIX), drive.wavefold),
    EffectKind("chorus", "Chorus",
               (modulation.CHORUS_RATE, modulation.CHORUS_DEPTH,
                modulation.CHORUS_MIX), modulation.chorus),
    EffectKind("tremolo", "Trémolo",
               (modulation.TREMOLO_RATE, modulation.TREMOLO_DEPTH,
                modulation.TREMOLO_SHAPE), modulation.tremolo),
    EffectKind("ringmod", "Modulation en anneau",
               (modulation.RING_FREQUENCY, modulation.RING_MIX),
               modulation.ring_modulator),
    EffectKind("delay", "Écho",
               (delay.TIME, delay.FEEDBACK, delay.MIX), delay.echo),
    EffectKind("bitcrush", "Réduction de définition",
               (bitcrush.BITS, bitcrush.DOWNSAMPLE, bitcrush.MIX), bitcrush.crush),
)

EFFECTS_BY_KEY: dict[str, EffectKind] = {kind.key: kind for kind in EFFECT_KINDS}

__all__ = [
    "EFFECTS_BY_KEY",
    "EFFECT_KINDS",
    "EffectKind",
    "apply_chain",
    "new_setting",
]


def new_setting(key: str) -> EffectSetting:
    """Crée un effet neuf, réglé sur ses valeurs de départ."""
    return EffectSetting(kind=key, values=default_values(EFFECTS_BY_KEY[key].parameters))


def apply_chain(
    signal: np.ndarray, sample_rate: int, chain: tuple[EffectSetting, ...]
) -> np.ndarray:
    """Applique les effets dans l'ordre de la chaîne et rend le signal traité."""
    for setting in chain:
        kind = EFFECTS_BY_KEY.get(setting.kind)
        if kind is None:
            continue
        signal = kind.process(signal, sample_rate, resolve(kind.parameters, setting.values))
    return signal
