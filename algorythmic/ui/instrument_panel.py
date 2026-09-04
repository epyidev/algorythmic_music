"""
Panneau des instruments : une couche à la fois, chacune gardant ses réglages.

@author epyidev
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..config.layer_settings import LayerSettings
from ..model.layers import LAYER_KEYS, LAYER_LABELS
from ..texts import LABEL_LAYER
from .layer_editor import LayerEditor


class InstrumentPanel(QWidget):
    """Sélecteur de couche et éditeur correspondant."""

    changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._editors = {key: LayerEditor(key, self) for key in LAYER_KEYS}
        self._stack = QStackedWidget(self)
        for key in LAYER_KEYS:
            self._editors[key].changed.connect(self.changed)
            self._stack.addWidget(self._editors[key])

        self._selector = QComboBox(self)
        for key in LAYER_KEYS:
            self._selector.addItem(LAYER_LABELS[key], key)
        self._selector.currentIndexChanged.connect(self._stack.setCurrentIndex)

        selector_row = QHBoxLayout()
        selector_row.setContentsMargins(0, 0, 0, 0)
        label = QLabel(LABEL_LAYER, self)
        label.setProperty("role", "subtitle")
        selector_row.addWidget(label)
        selector_row.addWidget(self._selector, 1)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(self._stack)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(selector_row)
        layout.addWidget(scroll, 1)

    def read_layers(self) -> dict[str, LayerSettings]:
        """Rend les réglages de toutes les couches."""
        return {key: editor.read_settings() for key, editor in self._editors.items()}
