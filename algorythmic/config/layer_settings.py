"""
Réglages propres à une couche : son timbre, sa chaîne d'effets, son niveau.

Ces objets ne sont que des données. Ils traversent l'application de
l'interface jusqu'au moteur sans jamais rien calculer eux-mêmes.

@author epyidev
"""

from __future__ import annotations

from dataclasses import dataclass, field

DEFAULT_VOICE_KIND = "additive"
NEUTRAL_AMOUNT = 1.0
NEUTRAL_CHARACTER = 0.5
MIN_LAYER_GAIN = 0.0
MAX_LAYER_GAIN = 2.0


@dataclass(frozen=True)
class Timbre:
    """Le type de voix d'une couche et ses quatre réglages communs."""

    kind: str = DEFAULT_VOICE_KIND
    brightness: float = NEUTRAL_AMOUNT
    detune: float = NEUTRAL_AMOUNT
    attack: float = NEUTRAL_AMOUNT
    character: float = NEUTRAL_CHARACTER


@dataclass(frozen=True)
class EffectSetting:
    """Un effet placé dans une chaîne, avec les valeurs de ses réglages."""

    kind: str
    values: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class LayerSettings:
    """Tout ce qui distingue une couche d'une autre au moment du rendu."""

    enabled: bool = True
    gain: float = NEUTRAL_AMOUNT
    timbre: Timbre = field(default_factory=Timbre)
    effects: tuple[EffectSetting, ...] = ()
