"""
Remontée de progression et demande d'annulation.

Le moteur ne connaît pas l'interface : il publie une étape et un ratio, et
c'est à l'appelant de traduire cette étape en texte lisible.

@author epyidev
"""

from __future__ import annotations

from enum import Enum
from typing import Callable

RATIO_FLOOR = 0.0
RATIO_CEILING = 1.0


class RenderStage(Enum):
    """Les étapes traversées par un rendu, dans leur ordre d'exécution."""

    PREPARING = "preparing"
    LAYERS = "layers"
    EFFECTS = "effects"
    AUTOMATION = "automation"
    REVERB = "reverb"
    SPECTRAL_TILT = "spectral_tilt"
    STEREO = "stereo"
    DYNAMICS = "dynamics"
    WRITING = "writing"
    DONE = "done"


class RenderCancelled(Exception):
    """Levée quand l'utilisateur interrompt un rendu en cours."""


class ProgressReporter:
    """Passerelle entre le moteur et ce qui observe son avancement."""

    def __init__(
        self,
        on_progress: Callable[[float, RenderStage], None] | None = None,
        cancel_requested: Callable[[], bool] | None = None,
    ) -> None:
        self._on_progress = on_progress
        self._cancel_requested = cancel_requested

    def report(self, ratio: float, stage: RenderStage) -> None:
        """Publie un avancement, puis vérifie qu'aucune annulation n'attend."""
        if self._on_progress is not None:
            bounded = min(max(ratio, RATIO_FLOOR), RATIO_CEILING)
            self._on_progress(bounded, stage)
        self.check()

    def check(self) -> None:
        """Interrompt le rendu si une annulation a été demandée."""
        if self._cancel_requested is not None and self._cancel_requested():
            raise RenderCancelled()
