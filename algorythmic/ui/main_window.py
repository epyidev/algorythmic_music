"""
Fenêtre principale : assemble les panneaux et pilote les fils de rendu.

@author epyidev
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from PySide6.QtCore import QThread, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .. import APPLICATION_VERSION
from ..config.track_settings import TrackSettings
from ..engine.preview import PreviewResult
from ..engine.progress import RenderStage
from ..engine.renderer import RenderResult
from ..model.arrangement import STRUCTURE_LABELS
from ..model.scale import MODE_LABELS, note_label
from ..texts import (
    BUTTON_CANCEL,
    BUTTON_OPEN_FOLDER,
    BUTTON_PLAY,
    BUTTON_PREVIEW,
    BUTTON_PREVIEW_STOP,
    BUTTON_RENDER,
    LOG_CANCELLED,
    LOG_DURATION,
    LOG_FAILED,
    LOG_FINISHED,
    LOG_NO_AUDIO_DEVICE,
    LOG_PREVIEW_READY,
    LOG_PREVIEW_STOPPED,
    LOG_STARTED,
    LOG_STRUCTURE,
    STAGE_LABELS,
    STATUS_CANCELLED,
    STATUS_CANCELLING,
    STATUS_PREVIEW_PLAYING,
    STATUS_PREVIEW_RENDERING,
    TAB_COMPOSITION,
    TAB_INSTRUMENTS,
    WINDOW_SUBTITLE,
    WINDOW_TITLE,
)
from .audio_player import AudioPlayer
from .instrument_panel import InstrumentPanel
from .preview_worker import PreviewWorker
from .progress_panel import ProgressPanel
from .render_worker import RenderWorker
from .settings_panel import SettingsPanel
from .theme import STYLE_SHEET

WINDOW_WIDTH = 1120
WINDOW_HEIGHT = 760
CONTENT_MARGIN = 18
COLUMN_SPACING = 18
SECONDS_PER_MINUTE = 60
SETTINGS_COLUMN_WEIGHT = 3
PROGRESS_COLUMN_WEIGHT = 2


class MainWindow(QMainWindow):
    """Le seul écran de l'application."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{WINDOW_TITLE} {APPLICATION_VERSION}")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(STYLE_SHEET)

        self._settings_panel = SettingsPanel(TrackSettings(), self)
        self._instrument_panel = InstrumentPanel(self)
        self._progress_panel = ProgressPanel(self)
        self._player = AudioPlayer(self)

        self._render_button = self._build_button(BUTTON_RENDER, "primary")
        self._preview_button = self._build_button(BUTTON_PREVIEW)
        self._cancel_button = self._build_button(BUTTON_CANCEL, "danger")
        self._open_folder_button = self._build_button(BUTTON_OPEN_FOLDER)
        self._play_button = self._build_button(BUTTON_PLAY)

        self._thread: QThread | None = None
        self._worker: RenderWorker | None = None
        self._preview_thread: QThread | None = None
        self._preview_worker: PreviewWorker | None = None
        self._last_output: Path | None = None

        self._cancel_button.setEnabled(False)
        self._open_folder_button.setEnabled(False)
        self._play_button.setEnabled(False)

        self._render_button.clicked.connect(self._start_render)
        self._preview_button.clicked.connect(self._toggle_preview)
        self._cancel_button.clicked.connect(self._cancel_render)
        self._open_folder_button.clicked.connect(self._open_output_folder)
        self._play_button.clicked.connect(self._play_output)
        self._player.stopped.connect(self._on_player_stopped)

        self.setCentralWidget(self._build_central_widget())

    def read_settings(self) -> TrackSettings:
        """Assemble les réglages généraux et ceux de chaque couche."""
        settings = self._settings_panel.read_settings()
        return replace(settings, layers=self._instrument_panel.read_layers())

    def _build_button(self, text: str, role: str | None = None) -> QPushButton:
        button = QPushButton(text, self)
        if role is not None:
            button.setProperty("role", role)
        return button

    def _build_central_widget(self) -> QWidget:
        title = QLabel(WINDOW_TITLE, self)
        title.setProperty("role", "title")
        subtitle = QLabel(WINDOW_SUBTITLE, self)
        subtitle.setProperty("role", "subtitle")

        tabs = QTabWidget(self)
        tabs.addTab(self._settings_panel, TAB_COMPOSITION)
        tabs.addTab(self._instrument_panel, TAB_INSTRUMENTS)

        actions = QHBoxLayout()
        actions.addWidget(self._render_button)
        actions.addWidget(self._preview_button)
        actions.addWidget(self._cancel_button)
        actions.addStretch()
        actions.addWidget(self._open_folder_button)
        actions.addWidget(self._play_button)

        right_column = QVBoxLayout()
        right_column.addWidget(self._progress_panel)
        right_column.addLayout(actions)

        columns = QHBoxLayout()
        columns.setSpacing(COLUMN_SPACING)
        columns.addWidget(tabs, SETTINGS_COLUMN_WEIGHT)
        columns.addLayout(right_column, PROGRESS_COLUMN_WEIGHT)

        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(
            CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN
        )
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(COLUMN_SPACING)
        layout.addLayout(columns)
        return central

    def _start_render(self) -> None:
        self._stop_preview()
        settings = self.read_settings()
        self._progress_panel.reset()
        self._progress_panel.append_log(LOG_STARTED.format(
            seed=settings.seed,
            tonic=note_label(settings.tonic_midi),
            mode=MODE_LABELS[settings.mode_name],
            bpm=settings.bpm,
        ))
        self._set_rendering(True)

        self._thread = QThread(self)
        self._worker = RenderWorker(settings)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.progressed.connect(self._on_progress)
        self._worker.succeeded.connect(self._on_succeeded)
        self._worker.cancelled.connect(self._on_cancelled)
        self._worker.failed.connect(self._on_failed)
        self._thread.start()

    def _cancel_render(self) -> None:
        if self._worker is not None:
            self._worker.request_cancel()
            self._cancel_button.setEnabled(False)
            self._progress_panel.set_status(STATUS_CANCELLING)

    def _on_progress(self, ratio: float, stage: RenderStage) -> None:
        self._progress_panel.update_progress(ratio, STAGE_LABELS[stage])

    def _on_succeeded(self, result: RenderResult) -> None:
        settings = self._settings_panel.read_settings()
        minutes, seconds = divmod(int(result.duration), SECONDS_PER_MINUTE)
        self._progress_panel.append_log(LOG_STRUCTURE.format(
            structure=STRUCTURE_LABELS[settings.structure_name],
            sections=result.section_count,
            events=result.event_count,
        ))
        self._progress_panel.append_log(LOG_DURATION.format(
            minutes=minutes, seconds=seconds
        ))
        self._progress_panel.append_log(LOG_FINISHED.format(path=result.output_path))

        self._last_output = Path(result.output_path)
        self._open_folder_button.setEnabled(True)
        self._play_button.setEnabled(True)
        self._finish_render()

    def _on_cancelled(self) -> None:
        self._progress_panel.append_log(LOG_CANCELLED)
        self._progress_panel.update_progress(0.0, STATUS_CANCELLED)
        self._finish_render()

    def _on_failed(self, reason: str) -> None:
        self._progress_panel.append_log(LOG_FAILED.format(reason=reason))
        self._finish_render()

    def _finish_render(self) -> None:
        self._thread, self._worker = self._shut_down(self._thread, self._worker)
        self._set_rendering(False)

    def _toggle_preview(self) -> None:
        if self._player.is_playing() or self._preview_worker is not None:
            self._stop_preview()
            return

        if not AudioPlayer.has_output_device():
            self._progress_panel.append_log(LOG_NO_AUDIO_DEVICE)
            return

        self._progress_panel.set_status(STATUS_PREVIEW_RENDERING)
        self._preview_button.setText(BUTTON_PREVIEW_STOP)

        self._preview_thread = QThread(self)
        self._preview_worker = PreviewWorker(self.read_settings())
        self._preview_worker.moveToThread(self._preview_thread)

        self._preview_thread.started.connect(self._preview_worker.run)
        self._preview_worker.succeeded.connect(self._on_preview_ready)
        self._preview_worker.cancelled.connect(self._stop_preview)
        self._preview_worker.failed.connect(self._on_preview_failed)
        self._preview_thread.start()

    def _on_preview_ready(self, result: PreviewResult) -> None:
        self._preview_thread, self._preview_worker = self._shut_down(
            self._preview_thread, self._preview_worker
        )
        if not self._player.play(result.frames, result.sample_rate):
            self._progress_panel.append_log(LOG_NO_AUDIO_DEVICE)
            self._preview_button.setText(BUTTON_PREVIEW)
            return

        self._progress_panel.set_status(STATUS_PREVIEW_PLAYING)
        self._progress_panel.append_log(
            LOG_PREVIEW_READY.format(seconds=result.duration)
        )

    def _on_preview_failed(self, reason: str) -> None:
        self._progress_panel.append_log(LOG_FAILED.format(reason=reason))
        self._stop_preview()

    def _stop_preview(self) -> None:
        if self._preview_worker is not None:
            self._preview_worker.request_cancel()
        self._preview_thread, self._preview_worker = self._shut_down(
            self._preview_thread, self._preview_worker
        )
        self._player.stop()
        self._preview_button.setText(BUTTON_PREVIEW)

    def _on_player_stopped(self) -> None:
        self._preview_button.setText(BUTTON_PREVIEW)
        self._progress_panel.append_log(LOG_PREVIEW_STOPPED)

    @staticmethod
    def _shut_down(thread: QThread | None, worker):
        """Arrête un fil de travail et libère son objet, dans cet ordre."""
        if thread is not None:
            thread.quit()
            thread.wait()
            thread.deleteLater()
        if worker is not None:
            worker.deleteLater()
        return None, None

    def _set_rendering(self, rendering: bool) -> None:
        self._settings_panel.setEnabled(not rendering)
        self._instrument_panel.setEnabled(not rendering)
        self._render_button.setEnabled(not rendering)
        self._preview_button.setEnabled(not rendering)
        self._cancel_button.setEnabled(rendering)

    def _open_output_folder(self) -> None:
        if self._last_output is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._last_output.parent)))

    def _play_output(self) -> None:
        if self._last_output is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._last_output)))

    def closeEvent(self, event) -> None:
        """Attend la fin des fils de travail avant de laisser la fenêtre se fermer."""
        self._player.stop()
        for worker in (self._worker, self._preview_worker):
            if worker is not None:
                worker.request_cancel()
        for thread in (self._thread, self._preview_thread):
            if thread is not None:
                thread.quit()
                thread.wait()
        super().closeEvent(event)
