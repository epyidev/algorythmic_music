"""
Curseur construit à partir de la déclaration d'un réglage.

Un effet qui ajoute un réglage à sa liste voit son curseur apparaître sans
qu'une seule ligne d'interface soit touchée.

@author epyidev
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSlider, QWidget

from ..synthesis.parameters import Parameter

SLIDER_STEPS = 1000
NAME_LABEL_WIDTH = 96
VALUE_LABEL_WIDTH = 74


class ParameterSlider(QWidget):
    """Un réglage nommé, réglable, dont la valeur courante reste visible."""

    changed = Signal()

    def __init__(
        self, parameter: Parameter, value: float, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._parameter = parameter

        name_label = QLabel(parameter.label, self)
        name_label.setProperty("role", "subtitle")
        name_label.setMinimumWidth(NAME_LABEL_WIDTH)

        self._slider = QSlider(Qt.Orientation.Horizontal, self)
        self._slider.setRange(0, SLIDER_STEPS)
        self._slider.setValue(self._to_steps(parameter.clamp(value)))

        self._value_label = QLabel(self)
        self._value_label.setProperty("role", "value")
        self._value_label.setMinimumWidth(VALUE_LABEL_WIDTH)
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(name_label)
        layout.addWidget(self._slider)
        layout.addWidget(self._value_label)

        self._slider.valueChanged.connect(self._on_slider_changed)
        self._refresh_label()

    def value(self) -> float:
        """Rend la valeur courante du réglage."""
        span = self._parameter.maximum - self._parameter.minimum
        return self._parameter.minimum + span * self._slider.value() / SLIDER_STEPS

    def _to_steps(self, value: float) -> int:
        span = self._parameter.maximum - self._parameter.minimum
        if span <= 0:
            return 0
        return int((value - self._parameter.minimum) / span * SLIDER_STEPS)

    def _on_slider_changed(self) -> None:
        self._refresh_label()
        self.changed.emit()

    def _refresh_label(self) -> None:
        text = f"{self.value():.{self._parameter.decimals}f}{self._parameter.unit}"
        self._value_label.setText(text)
