"""
Grille rythmique et flou de placement.

Rien ne tombe exactement sur la grille : c'est ce décalage aléatoire qui
donne la pulsation trouble du morceau, et il est le seul responsable de
l'absence de sensation de clic.

@author epyidev
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

BASE_JITTER_SECONDS = 0.042
VELOCITY_JITTER = 0.15


@dataclass(frozen=True)
class Timing:
    """Durée du temps et amplitude des écarts appliqués à chaque note."""

    beat_duration: float
    jitter_seconds: float
    velocity_jitter: float

    def offset(self, rng: np.random.Generator, scale: float = 1.0) -> float:
        """Tire un décalage temporel autour de la position théorique."""
        return float(rng.normal(0.0, self.jitter_seconds * scale))

    def amplitude(self, rng: np.random.Generator, base: float) -> float:
        """Tire une amplitude autour de la vélocité nominale."""
        return base * (1.0 + float(rng.normal(0.0, self.velocity_jitter)))


def build_timing(beat_duration: float, looseness: float) -> Timing:
    """Construit la grille à partir du tempo et du degré de flou voulu."""
    return Timing(
        beat_duration=beat_duration,
        jitter_seconds=BASE_JITTER_SECONDS * looseness,
        velocity_jitter=VELOCITY_JITTER,
    )
