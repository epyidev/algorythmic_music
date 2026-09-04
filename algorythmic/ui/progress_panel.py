"""
Panneau de progression : barre d'avancement, étape en cours et journal.

@author epyidev
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from ..texts import GROUP_PROGRESS, STATUS_IDLE

PROGRESS_SCALE = 100
LOG_MINIMUM_HEIGHT = 140
MAX_LOG_BLOCKS = 500


class ProgressPanel(QWidget):
    """Affiche où en est le rendu et ce qu'il a fait jusque-là."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._bar = QProgressBar(self)
        self._bar.setRange(0, PROGRESS_SCALE)
        self._bar.setValue(0)

        self._status = QLabel(STATUS_IDLE, self)
        self._status.setProperty("role", "subtitle")

        self._log = QPlainTextEdit(self)
        self._log.setReadOnly(True)
        self._log.setMinimumHeight(LOG_MINIMUM_HEIGHT)
        self._log.setMaximumBlockCount(MAX_LOG_BLOCKS)

        group = QGroupBox(GROUP_PROGRESS, self)
        inner = QVBoxLayout(group)
        inner.addWidget(self._bar)
        inner.addWidget(self._status)
        inner.addWidget(self._log)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(group)

    def update_progress(self, ratio: float, stage_label: str) -> None:
        """Positionne la barre et nomme l'étape en cours."""
        self._bar.setValue(int(ratio * PROGRESS_SCALE))
        self._status.setText(stage_label)

    def set_status(self, message: str) -> None:
        """Remplace le texte d'état sans toucher à la barre."""
        self._status.setText(message)

    def append_log(self, message: str) -> None:
        """Ajoute une ligne au journal et fait défiler jusqu'à elle."""
        self._log.appendPlainText(message)

    def reset(self) -> None:
        """Remet le panneau dans son état de départ."""
        self._bar.setValue(0)
        self._status.setText(STATUS_IDLE)
        self._log.clear()
