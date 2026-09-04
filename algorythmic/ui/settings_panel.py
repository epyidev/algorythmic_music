"""
Panneau des réglages : tout ce que l'utilisateur choisit avant un rendu.

@author epyidev
"""

from __future__ import annotations

import random
from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..config.track_settings import (
    MAX_AMOUNT,
    MAX_BLEND_SECONDS,
    MAX_BPM,
    MAX_SEED,
    MAX_TONIC_MIDI,
    MIN_AMOUNT,
    MIN_BLEND_SECONDS,
    MIN_BPM,
    MIN_SEED,
    MIN_TONIC_MIDI,
    TrackSettings,
)
from ..model.arrangement import STRUCTURE_LABELS
from ..model.scale import MODE_LABELS, note_label
from ..synthesis.parameters import Parameter
from ..texts import (
    BUTTON_BROWSE,
    BUTTON_RANDOM_SEED,
    DIALOG_SAVE_FILTER,
    DIALOG_SAVE_TITLE,
    GROUP_COMPOSITION,
    GROUP_OUTPUT,
    GROUP_TEXTURE,
    GROUP_TRANSITIONS,
    LABEL_HARD_CUT,
    LABEL_LOOSENESS,
    LABEL_MODE,
    LABEL_OUTPUT_FILE,
    LABEL_REVERB,
    LABEL_SEED,
    LABEL_SECTION_BLEND,
    LABEL_SPECTRAL_TILT,
    LABEL_STEREO_WIDTH,
    LABEL_STRUCTURE,
    LABEL_TEMPO,
    LABEL_TONIC,
    SECONDS_SUFFIX,
    TEMPO_SUFFIX,
)
from .parameter_slider import ParameterSlider
from .ratio_slider import RatioSlider

TEMPO_STEP = 0.5
TEMPO_DECIMALS = 1
SECTION_BLEND = Parameter("section_blend", LABEL_SECTION_BLEND,
                          MIN_BLEND_SECONDS, MAX_BLEND_SECONDS, 0.9,
                          SECONDS_SUFFIX)


class SettingsPanel(QWidget):
    """Collecte les réglages et sait les rendre sous forme de TrackSettings."""

    def __init__(self, defaults: TrackSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._seed = self._build_seed_spin(defaults)
        self._tonic = self._build_tonic_combo(defaults)
        self._mode = self._build_keyed_combo(MODE_LABELS, defaults.mode_name)
        self._tempo = self._build_tempo_spin(defaults)
        self._structure = self._build_keyed_combo(
            STRUCTURE_LABELS, defaults.structure_name
        )
        self._spectral_tilt = RatioSlider(
            MIN_AMOUNT, MAX_AMOUNT, defaults.spectral_tilt
        )
        self._reverb = RatioSlider(MIN_AMOUNT, MAX_AMOUNT, defaults.reverb_amount)
        self._stereo_width = RatioSlider(MIN_AMOUNT, MAX_AMOUNT, defaults.stereo_width)
        self._looseness = RatioSlider(
            MIN_AMOUNT, MAX_AMOUNT, defaults.timing_looseness
        )
        self._hard_cut = RatioSlider(MIN_AMOUNT, MAX_AMOUNT, defaults.hard_cut_amount)
        self._section_blend = ParameterSlider(
            SECTION_BLEND, defaults.section_blend, self
        )
        self._output_path = QLineEdit(str(defaults.output_path.resolve()), self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._build_composition_group())
        layout.addWidget(self._build_texture_group())
        layout.addWidget(self._build_transitions_group())
        layout.addWidget(self._build_output_group())
        layout.addStretch()

    def read_settings(self) -> TrackSettings:
        """Rend les réglages courants, bornés."""
        return TrackSettings(
            seed=self._seed.value(),
            tonic_midi=self._tonic.currentData(),
            mode_name=self._mode.currentData(),
            bpm=self._tempo.value(),
            structure_name=self._structure.currentData(),
            spectral_tilt=self._spectral_tilt.value(),
            reverb_amount=self._reverb.value(),
            stereo_width=self._stereo_width.value(),
            timing_looseness=self._looseness.value(),
            hard_cut_amount=self._hard_cut.value(),
            section_blend=self._section_blend.value(),
            output_path=Path(self._output_path.text()),
        ).clamped()

    def set_enabled_for_render(self, enabled: bool) -> None:
        """Verrouille les réglages pendant qu'un rendu tourne."""
        self.setEnabled(enabled)

    def _build_seed_spin(self, defaults: TrackSettings) -> QSpinBox:
        spin = QSpinBox(self)
        spin.setRange(MIN_SEED, MAX_SEED)
        spin.setValue(defaults.seed)
        return spin

    def _build_tonic_combo(self, defaults: TrackSettings) -> QComboBox:
        combo = QComboBox(self)
        for midi in range(MIN_TONIC_MIDI, MAX_TONIC_MIDI + 1):
            combo.addItem(note_label(midi), midi)
        combo.setCurrentIndex(defaults.tonic_midi - MIN_TONIC_MIDI)
        return combo

    def _build_keyed_combo(self, labels: dict[str, str], current: str) -> QComboBox:
        combo = QComboBox(self)
        for key, label in labels.items():
            combo.addItem(label, key)
        combo.setCurrentIndex(list(labels).index(current))
        return combo

    def _build_tempo_spin(self, defaults: TrackSettings) -> QDoubleSpinBox:
        spin = QDoubleSpinBox(self)
        spin.setRange(MIN_BPM, MAX_BPM)
        spin.setDecimals(TEMPO_DECIMALS)
        spin.setSingleStep(TEMPO_STEP)
        spin.setSuffix(TEMPO_SUFFIX)
        spin.setValue(defaults.bpm)
        return spin

    def _build_composition_group(self) -> QGroupBox:
        group = QGroupBox(GROUP_COMPOSITION, self)
        form = QFormLayout(group)

        random_button = QPushButton(BUTTON_RANDOM_SEED, group)
        random_button.clicked.connect(self._draw_random_seed)
        seed_row = QHBoxLayout()
        seed_row.setContentsMargins(0, 0, 0, 0)
        seed_row.addWidget(self._seed)
        seed_row.addWidget(random_button)

        form.addRow(LABEL_SEED, seed_row)
        form.addRow(LABEL_TONIC, self._tonic)
        form.addRow(LABEL_MODE, self._mode)
        form.addRow(LABEL_TEMPO, self._tempo)
        form.addRow(LABEL_STRUCTURE, self._structure)
        return group

    def _build_texture_group(self) -> QGroupBox:
        group = QGroupBox(GROUP_TEXTURE, self)
        form = QFormLayout(group)
        form.addRow(LABEL_SPECTRAL_TILT, self._spectral_tilt)
        form.addRow(LABEL_REVERB, self._reverb)
        form.addRow(LABEL_STEREO_WIDTH, self._stereo_width)
        form.addRow(LABEL_LOOSENESS, self._looseness)
        return group

    def _build_transitions_group(self) -> QGroupBox:
        group = QGroupBox(GROUP_TRANSITIONS, self)
        form = QFormLayout(group)
        form.addRow(LABEL_HARD_CUT, self._hard_cut)
        form.addRow(self._section_blend)
        return group

    def _build_output_group(self) -> QGroupBox:
        group = QGroupBox(GROUP_OUTPUT, self)
        form = QFormLayout(group)

        browse_button = QPushButton(BUTTON_BROWSE, group)
        browse_button.clicked.connect(self._choose_output_path)
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(self._output_path)
        row.addWidget(browse_button)

        form.addRow(LABEL_OUTPUT_FILE, row)
        return group

    def _draw_random_seed(self) -> None:
        self._seed.setValue(random.randint(MIN_SEED, MAX_SEED))

    def _choose_output_path(self) -> None:
        chosen, _ = QFileDialog.getSaveFileName(
            self, DIALOG_SAVE_TITLE, self._output_path.text(), DIALOG_SAVE_FILTER
        )
        if chosen:
            self._output_path.setText(chosen)
