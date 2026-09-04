"""
Curseur de dosage, gradué en pourcentage.

@author epyidev
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSlider, QWidget

from ..texts import PERCENT_SUFFIX

PERCENT_SCALE = 100.0
TICK_INTERVAL = 25
VALUE_LABEL_WIDTH = 46


class RatioSlider(QWidget):
    """Un curseur horizontal dont la valeur s'affiche à droite."""

    def __init__(
        self,
        minimum: float,
        maximum: float,
        value: float,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._slider = QSlider(Qt.Orientation.Horizontal, self)
        self._slider.setRange(
            int(minimum * PERCENT_SCALE), int(maximum * PERCENT_SCALE)
        )
        self._slider.setValue(int(value * PERCENT_SCALE))
        self._slider.setTickInterval(TICK_INTERVAL)

        self._value_label = QLabel(self)
        self._value_label.setProperty("role", "value")
        self._value_label.setMinimumWidth(VALUE_LABEL_WIDTH)
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._slider)
        layout.addWidget(self._value_label)

        self._slider.valueChanged.connect(self._refresh_label)
        self._refresh_label(self._slider.value())

    def value(self) -> float:
        """Rend le dosage courant, où cent pour cent vaut un."""
        return self._slider.value() / PERCENT_SCALE

    def _refresh_label(self, raw_value: int) -> None:
        self._value_label.setText(f"{raw_value}{PERCENT_SUFFIX}")
