"""
Rendu d'un extrait de préécoute dans un fil séparé.

Même si l'extrait est court, il reste plusieurs centaines de milliers
d'échantillons : le calculer sur le fil de l'interface ferait sauter le
curseur qu'on vient de bouger.

@author epyidev
"""

from __future__ import annotations

import threading

from PySide6.QtCore import QObject, Signal, Slot

from ..config.track_settings import TrackSettings
from ..engine.preview import render_preview
from ..engine.progress import ProgressReporter, RenderCancelled


class PreviewWorker(QObject):
    """Porte le rendu d'un extrait et le rend sous forme d'échantillons."""

    succeeded = Signal(object)
    cancelled = Signal()
    failed = Signal(str)

    def __init__(self, settings: TrackSettings) -> None:
        super().__init__()
        self._settings = settings
        self._cancel_event = threading.Event()

    def request_cancel(self) -> None:
        """Demande l'abandon de l'extrait en cours."""
        self._cancel_event.set()

    @Slot()
    def run(self) -> None:
        """Point d'entrée exécuté sur le fil de préécoute."""
        reporter = ProgressReporter(cancel_requested=self._cancel_event.is_set)
        try:
            self.succeeded.emit(render_preview(self._settings, reporter))
        except RenderCancelled:
            self.cancelled.emit()
        except Exception as error:
            self.failed.emit(str(error))
