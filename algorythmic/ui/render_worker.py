"""
Exécution d'un rendu dans un fil séparé.

Le rendu dure plusieurs dizaines de secondes : le laisser sur le fil de
l'interface gèlerait la fenêtre et empêcherait toute annulation.

@author epyidev
"""

from __future__ import annotations

import threading

from PySide6.QtCore import QObject, Signal, Slot

from ..config.track_settings import TrackSettings
from ..engine.progress import ProgressReporter, RenderCancelled
from ..engine.renderer import render_track


class RenderWorker(QObject):
    """Porte un rendu du début à la fin et publie son avancement."""

    progressed = Signal(float, object)
    succeeded = Signal(object)
    cancelled = Signal()
    failed = Signal(str)

    def __init__(self, settings: TrackSettings) -> None:
        super().__init__()
        self._settings = settings
        self._cancel_event = threading.Event()

    def request_cancel(self) -> None:
        """Demande l'arrêt du rendu, honoré à la prochaine étape."""
        self._cancel_event.set()

    @Slot()
    def run(self) -> None:
        """Point d'entrée exécuté sur le fil de rendu."""
        reporter = ProgressReporter(
            on_progress=lambda ratio, stage: self.progressed.emit(ratio, stage),
            cancel_requested=self._cancel_event.is_set,
        )
        try:
            self.succeeded.emit(render_track(self._settings, reporter))
        except RenderCancelled:
            self.cancelled.emit()
        except Exception as error:
            self.failed.emit(str(error))
