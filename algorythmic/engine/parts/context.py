"""
Contexte commun passé à chaque partie instrumentale.

@author epyidev
"""

from __future__ import annotations

from dataclasses import dataclass

from ...config.layer_settings import LayerSettings
from ...model.timing import Timing


@dataclass(frozen=True)
class PartContext:
    """Ce qu'une partie doit connaître en plus de l'accord qu'elle joue."""

    timing: Timing
    sample_rate: int
    tonic_midi: int
    mode_name: str
    slot_duration: float
    layer: LayerSettings
