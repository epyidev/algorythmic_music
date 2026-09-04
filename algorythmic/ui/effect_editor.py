"""
Un effet posé dans une chaîne, avec ses réglages et sa place dans l'ordre.

@author epyidev
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ..config.layer_settings import EffectSetting
from ..synthesis.effects import EffectKind
from ..synthesis.parameters import resolve
from ..texts import BUTTON_MOVE_DOWN, BUTTON_MOVE_UP, BUTTON_REMOVE_EFFECT
from .parameter_slider import ParameterSlider

MOVE_UP = -1
MOVE_DOWN = 1
BUTTON_WIDTH = 84


class EffectEditor(QFrame):
    """Le bloc de réglages d'un effet, avec ses commandes de déplacement."""

    changed = Signal()
    removed = Signal(object)
    moved = Signal(object, int)

    def __init__(self, kind: EffectKind, values: dict[str, float]) -> None:
        super().__init__()
        self._kind = kind
        self.setProperty("role", "card")

        resolved = resolve(kind.parameters, values)
        self._sliders = [
            ParameterSlider(parameter, resolved[parameter.name], self)
            for parameter in kind.parameters
        ]

        layout = QVBoxLayout(self)
        layout.addLayout(self._build_header())
        for slider in self._sliders:
            slider.changed.connect(self.changed)
            layout.addWidget(slider)

    def kind_key(self) -> str:
        """Rend l'identifiant de l'effet représenté."""
        return self._kind.key

    def read_setting(self) -> EffectSetting:
        """Rend l'effet et ses valeurs courantes."""
        values = {
            parameter.name: slider.value()
            for parameter, slider in zip(self._kind.parameters, self._sliders)
        }
        return EffectSetting(kind=self._kind.key, values=values)

    def _build_header(self) -> QHBoxLayout:
        title = QLabel(self._kind.label, self)
        title.setStyleSheet("font-weight: 600;")

        up_button = QPushButton(BUTTON_MOVE_UP, self)
        down_button = QPushButton(BUTTON_MOVE_DOWN, self)
        remove_button = QPushButton(BUTTON_REMOVE_EFFECT, self)
        remove_button.setProperty("role", "danger")

        for button in (up_button, down_button, remove_button):
            button.setFixedWidth(BUTTON_WIDTH)

        up_button.clicked.connect(lambda: self.moved.emit(self, MOVE_UP))
        down_button.clicked.connect(lambda: self.moved.emit(self, MOVE_DOWN))
        remove_button.clicked.connect(lambda: self.removed.emit(self))

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(up_button)
        header.addWidget(down_button)
        header.addWidget(remove_button)
        return header
