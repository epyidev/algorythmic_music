"""
Lecture en boucle d'un extrait déjà rendu.

Les échantillons sont joués depuis la mémoire, sans passer par un fichier
temporaire. La boucle est relancée depuis la file d'événements plutôt que
depuis le signal de changement d'état : redémarrer la sortie audio depuis son
propre gestionnaire d'état la laisserait dans un état incohérent.

@author epyidev
"""

from __future__ import annotations

from PySide6.QtCore import QBuffer, QByteArray, QObject, QTimer, Signal, Slot
from PySide6.QtMultimedia import QAudio, QAudioFormat, QAudioSink, QMediaDevices

from ..config.audio_format import CHANNEL_COUNT

RESTART_DELAY_MS = 0


class AudioPlayer(QObject):
    """Joue un extrait en boucle sur la sortie audio par défaut."""

    stopped = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._sink: QAudioSink | None = None
        self._buffer: QBuffer | None = None
        self._looping = False

    @staticmethod
    def has_output_device() -> bool:
        """Dit si le poste dispose d'une sortie audio utilisable."""
        return not QMediaDevices.defaultAudioOutput().isNull()

    def is_playing(self) -> bool:
        """Dit si un extrait est en cours de lecture."""
        return self._looping

    def play(self, frames: bytes, sample_rate: int) -> bool:
        """Démarre la lecture en boucle et dit si la sortie a pu être ouverte."""
        self.stop()

        device = QMediaDevices.defaultAudioOutput()
        if device.isNull():
            return False

        audio_format = QAudioFormat()
        audio_format.setSampleRate(sample_rate)
        audio_format.setChannelCount(CHANNEL_COUNT)
        audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)
        if not device.isFormatSupported(audio_format):
            return False

        self._buffer = QBuffer(self)
        self._buffer.setData(QByteArray(frames))
        self._buffer.open(QBuffer.OpenModeFlag.ReadOnly)

        self._sink = QAudioSink(device, audio_format, self)
        self._sink.stateChanged.connect(self._on_state_changed)
        self._looping = True
        self._sink.start(self._buffer)
        return True

    def stop(self) -> None:
        """Coupe la lecture et libère la sortie audio."""
        was_playing = self._looping
        self._looping = False

        if self._sink is not None:
            self._sink.stateChanged.disconnect(self._on_state_changed)
            self._sink.stop()
            self._sink.deleteLater()
            self._sink = None
        if self._buffer is not None:
            self._buffer.close()
            self._buffer.deleteLater()
            self._buffer = None

        if was_playing:
            self.stopped.emit()

    @Slot(QAudio.State)
    def _on_state_changed(self, state: QAudio.State) -> None:
        """Relance la lecture quand la sortie a vidé son tampon."""
        if self._looping and state == QAudio.State.IdleState:
            QTimer.singleShot(RESTART_DELAY_MS, self._restart)

    def _restart(self) -> None:
        if not self._looping or self._sink is None or self._buffer is None:
            return
        self._buffer.seek(0)
        self._sink.start(self._buffer)
