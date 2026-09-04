"""
Fenêtre principale : assemble les panneaux et pilote le fil de rendu.

@author epyidev
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import APPLICATION_VERSION
from ..config.track_settings import TrackSettings
from ..engine.progress import RenderStage
from ..engine.renderer import RenderResult
from ..model.arrangement import STRUCTURE_LABELS
from ..model.scale import MODE_LABELS, note_label
from ..texts import (
    BUTTON_CANCEL,
    BUTTON_OPEN_FOLDER,
    BUTTON_PLAY,
    BUTTON_RENDER,
    LOG_CANCELLED,
    LOG_DURATION,
    LOG_FAILED,
    LOG_FINISHED,
    LOG_STARTED,
    LOG_STRUCTURE,
    STAGE_LABELS,
    STATUS_CANCELLED,
    STATUS_CANCELLING,
    WINDOW_SUBTITLE,
    WINDOW_TITLE,
)
from .progress_panel import ProgressPanel
from .render_worker import RenderWorker
from .settings_panel import SettingsPanel
from .theme import STYLE_SHEET

WINDOW_WIDTH = 940
WINDOW_HEIGHT = 620
CONTENT_MARGIN = 18
COLUMN_SPACING = 18
SECONDS_PER_MINUTE = 60


class MainWindow(QMainWindow):
    """Le seul écran de l'application."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{WINDOW_TITLE} {APPLICATION_VERSION}")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(STYLE_SHEET)

        self._settings_panel = SettingsPanel(TrackSettings(), self)
        self._progress_panel = ProgressPanel(self)
        self._render_button = self._build_button(BUTTON_RENDER, "primary")
        self._cancel_button = self._build_button(BUTTON_CANCEL, "danger")
        self._open_folder_button = self._build_button(BUTTON_OPEN_FOLDER)
        self._play_button = self._build_button(BUTTON_PLAY)

        self._thread: QThread | None = None
        self._worker: RenderWorker | None = None
        self._last_output: Path | None = None

        self._cancel_button.setEnabled(False)
        self._open_folder_button.setEnabled(False)
        self._play_button.setEnabled(False)

        self._render_button.clicked.connect(self._start_render)
        self._cancel_button.clicked.connect(self._cancel_render)
        self._open_folder_button.clicked.connect(self._open_output_folder)
        self._play_button.clicked.connect(self._play_output)

        self.setCentralWidget(self._build_central_widget())

    def _build_button(self, text: str, role: str | None = None) -> QPushButton:
        button = QPushButton(text, self)
        if role is not None:
            button.setProperty("role", role)
        return button

    def _build_central_widget(self) -> QWidget:
        title = QLabel(WINDOW_TITLE, self)
        title.setStyleSheet("font-size: 20px; font-weight: 600;")
        subtitle = QLabel(WINDOW_SUBTITLE, self)
        subtitle.setProperty("role", "subtitle")

        actions = QHBoxLayout()
        actions.addWidget(self._render_button)
        actions.addWidget(self._cancel_button)
        actions.addStretch()
        actions.addWidget(self._open_folder_button)
        actions.addWidget(self._play_button)

        right_column = QVBoxLayout()
        right_column.addWidget(self._progress_panel)
        right_column.addLayout(actions)

        columns = QHBoxLayout()
        columns.setSpacing(COLUMN_SPACING)
        columns.addWidget(self._settings_panel, 1)
        columns.addLayout(right_column, 1)

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
        settings = self._settings_panel.read_settings()
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
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait()
            self._thread.deleteLater()
        if self._worker is not None:
            self._worker.deleteLater()
        self._thread = None
        self._worker = None
        self._set_rendering(False)

    def _set_rendering(self, rendering: bool) -> None:
        self._settings_panel.set_enabled_for_render(not rendering)
        self._render_button.setEnabled(not rendering)
        self._cancel_button.setEnabled(rendering)

    def _open_output_folder(self) -> None:
        if self._last_output is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._last_output.parent)))

    def _play_output(self) -> None:
        if self._last_output is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._last_output)))

    def closeEvent(self, event) -> None:
        """Attend la fin du fil de rendu avant de laisser la fenêtre se fermer."""
        if self._worker is not None:
            self._worker.request_cancel()
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait()
        super().closeEvent(event)
