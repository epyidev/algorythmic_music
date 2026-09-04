"""
Réglages d'un timbre indépendants de la hauteur et de la durée.

Le vibrato est calculé en intégrant la fréquence instantanée, et une seule
fois pour toute la voix. Les deux points comptent : multiplier le temps par
un facteur qui varie ferait dériver la hauteur tout au long de la note, et
donner à chaque partiel son propre vibrato désaccorderait la série
harmonique d'une même voix. Sur un instrument réel, le vibrato déplace tous
les partiels ensemble.

@author epyidev
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

FULL_TURN = 2.0 * np.pi
NYQUIST_MARGIN = 0.45


@dataclass(frozen=True)
class VoiceSpec:
    """Ce qu'une partie impose à sa voix, avant les réglages de l'utilisateur."""

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


def vibrato_excursion(
    time: np.ndarray, depth: float, rate: float, offset: float
) -> np.ndarray:
    """Rend l'écart de phase, en secondes, dû au vibrato.

    C'est l'intégrale exacte de la déviation de fréquence. La phase d'un
    partiel de fréquence f vaut alors 2 pi f fois le temps augmenté de cet
    écart, ce qui laisse la hauteur moyenne du partiel inchangée.
    """
    if depth <= 0.0 or rate <= 0.0:
        return np.zeros(len(time))
    angular = FULL_TURN * rate
    return depth / angular * (np.cos(offset) - np.cos(angular * time + offset))


def highest_audible_rank(fundamental: float, sample_rate: int, wanted: int) -> int:
    """Limite le nombre de partiels pour qu'aucun ne dépasse la bande utile."""
    ceiling = int(sample_rate * NYQUIST_MARGIN / max(fundamental, 1.0))
    return max(1, min(wanted, ceiling))
