"""
Les réglages d'une couche : son niveau, son timbre et sa chaîne d'effets.

@author epyidev
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..config.layer_settings import (
    MAX_LAYER_GAIN,
    MIN_LAYER_GAIN,
    LayerSettings,
    Timbre,
)
from ..model.layers import LAYERS_WITH_TIMBRE
from ..synthesis.effects import EFFECTS_BY_KEY, EFFECT_KINDS, new_setting
from ..synthesis.parameters import Parameter
from ..synthesis.voices import VOICE_LABELS
from ..texts import (
    BUTTON_ADD_EFFECT,
    DRUMS_WITHOUT_TIMBRE,
    EFFECTS_EMPTY,
    GROUP_EFFECTS,
    GROUP_VOICE,
    LABEL_ATTACK,
    LABEL_BRIGHTNESS,
    LABEL_CHARACTER,
    LABEL_DETUNE,
    LABEL_LAYER_ENABLED,
    LABEL_LAYER_GAIN,
    LABEL_TIMBRE,
)
from .effect_editor import EffectEditor
from .parameter_slider import ParameterSlider

GAIN = Parameter("gain", LABEL_LAYER_GAIN, MIN_LAYER_GAIN, MAX_LAYER_GAIN, 1.0)
BRIGHTNESS = Parameter("brightness", LABEL_BRIGHTNESS, 0.0, 2.0, 1.0)
DETUNE = Parameter("detune", LABEL_DETUNE, 0.0, 4.0, 1.0)
ATTACK = Parameter("attack", LABEL_ATTACK, 0.05, 4.0, 1.0)
CHARACTER = Parameter("character", LABEL_CHARACTER, 0.0, 1.0, 0.5)


class LayerEditor(QWidget):
    """Tout ce qui se règle sur une seule couche."""

    changed = Signal()

    def __init__(self, layer_key: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layer_key = layer_key
        self._has_timbre = layer_key in LAYERS_WITH_TIMBRE

        self._enabled = QCheckBox(LABEL_LAYER_ENABLED, self)
        self._enabled.setChecked(True)
        self._enabled.stateChanged.connect(self.changed)

        self._gain = ParameterSlider(GAIN, GAIN.default, self)
        self._gain.changed.connect(self.changed)

        self._timbre_kind = QComboBox(self)
        for key, label in VOICE_LABELS.items():
            self._timbre_kind.addItem(label, key)
        self._timbre_kind.currentIndexChanged.connect(self.changed)

        self._timbre_sliders = {
            "brightness": ParameterSlider(BRIGHTNESS, BRIGHTNESS.default, self),
            "detune": ParameterSlider(DETUNE, DETUNE.default, self),
            "attack": ParameterSlider(ATTACK, ATTACK.default, self),
            "character": ParameterSlider(CHARACTER, CHARACTER.default, self),
        }
        for slider in self._timbre_sliders.values():
            slider.changed.connect(self.changed)

        self._effect_editors: list[EffectEditor] = []
        self._effects_layout = QVBoxLayout()
        self._effects_layout.setContentsMargins(0, 0, 0, 0)
        self._empty_label = QLabel(EFFECTS_EMPTY, self)
        self._empty_label.setProperty("role", "subtitle")
        self._effects_layout.addWidget(self._empty_label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._enabled)
        layout.addWidget(self._gain)
        layout.addWidget(self._build_voice_group())
        layout.addWidget(self._build_effects_group())
        layout.addStretch()

    def read_settings(self) -> LayerSettings:
        """Rend les réglages courants de la couche."""
        return LayerSettings(
            enabled=self._enabled.isChecked(),
            gain=self._gain.value(),
            timbre=Timbre(
                kind=self._timbre_kind.currentData(),
                brightness=self._timbre_sliders["brightness"].value(),
                detune=self._timbre_sliders["detune"].value(),
                attack=self._timbre_sliders["attack"].value(),
                character=self._timbre_sliders["character"].value(),
            ),
            effects=tuple(editor.read_setting() for editor in self._effect_editors),
        )

    def _build_voice_group(self) -> QGroupBox:
        group = QGroupBox(GROUP_VOICE, self)
        form = QFormLayout(group)

        if not self._has_timbre:
            notice = QLabel(DRUMS_WITHOUT_TIMBRE, group)
            notice.setProperty("role", "subtitle")
            notice.setWordWrap(True)
            form.addRow(notice)
            self._timbre_kind.setVisible(False)
            for slider in self._timbre_sliders.values():
                slider.setVisible(False)
            return group

        form.addRow(LABEL_TIMBRE, self._timbre_kind)
        for slider in self._timbre_sliders.values():
            form.addRow(slider)
        return group

    def _build_effects_group(self) -> QGroupBox:
        group = QGroupBox(GROUP_EFFECTS, self)

        self._effect_choice = QComboBox(group)
        for kind in EFFECT_KINDS:
            self._effect_choice.addItem(kind.label, kind.key)

        add_button = QPushButton(BUTTON_ADD_EFFECT, group)
        add_button.clicked.connect(self._add_selected_effect)

        chooser = QHBoxLayout()
        chooser.setContentsMargins(0, 0, 0, 0)
        chooser.addWidget(self._effect_choice)
        chooser.addWidget(add_button)

        layout = QVBoxLayout(group)
        layout.addLayout(chooser)
        layout.addLayout(self._effects_layout)
        return group

    def _add_selected_effect(self) -> None:
        setting = new_setting(self._effect_choice.currentData())
        self._insert_editor(EffectEditor(EFFECTS_BY_KEY[setting.kind], setting.values))
        self.changed.emit()

    def _insert_editor(self, editor: EffectEditor) -> None:
        editor.changed.connect(self.changed)
        editor.removed.connect(self._remove_editor)
        editor.moved.connect(self._move_editor)
        self._effect_editors.append(editor)
        self._effects_layout.addWidget(editor)
        self._empty_label.setVisible(False)

    def _remove_editor(self, editor: EffectEditor) -> None:
        self._effect_editors.remove(editor)
        self._effects_layout.removeWidget(editor)
        editor.setParent(None)
        editor.deleteLater()
        self._empty_label.setVisible(not self._effect_editors)
        self.changed.emit()

    def _move_editor(self, editor: EffectEditor, direction: int) -> None:
        index = self._effect_editors.index(editor)
        target = index + direction
        if not 0 <= target < len(self._effect_editors):
            return

        self._effect_editors.pop(index)
        self._effect_editors.insert(target, editor)
        self._effects_layout.removeWidget(editor)
        # Le libellé de vide occupe la première position du conteneur.
        self._effects_layout.insertWidget(target + 1, editor)
        self.changed.emit()
