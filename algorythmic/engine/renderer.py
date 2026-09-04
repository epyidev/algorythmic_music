"""
Enchaînement complet d'un rendu, de la graine au fichier écrit.

@author epyidev
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ..audio_io.wave_writer import write_wave
from ..config.audio_format import SAMPLE_RATE
from ..config.track_settings import TrackSettings
from ..model.arrangement import Section
from ..model.progression import build_progression
from .automation import build_automation
from .layer_builder import build_layers
from .mixer import mix
from .progress import ProgressReporter, RenderStage
from .timeline import LEAD_IN_SILENCE, TAIL_SILENCE, Timeline, build_timeline

PREPARING_PROGRESS = 0.02
AUTOMATION_PROGRESS = 0.58
WRITING_PROGRESS = 0.97
DONE_PROGRESS = 1.0
MIX_SEED_OFFSET = 1


@dataclass(frozen=True)
class RenderResult:
    """Ce qu'un rendu laisse derrière lui."""

    output_path: Path
    duration: float
    section_count: int
    event_count: int


def render_stereo(
    settings: TrackSettings,
    reporter: ProgressReporter,
    sample_rate: int = SAMPLE_RATE,
    sections: tuple[Section, ...] | None = None,
    lead_in: float = LEAD_IN_SILENCE,
    tail: float = TAIL_SILENCE,
) -> tuple[np.ndarray, Timeline]:
    """Produit le mixage stéréo et la grille dont il est issu."""
    reporter.report(PREPARING_PROGRESS, RenderStage.PREPARING)

    progression = build_progression(settings.tonic_midi, settings.mode_name)
    timeline = build_timeline(settings, progression, sections, lead_in, tail)
    layers = build_layers(settings, timeline, sample_rate, reporter)

    reporter.report(AUTOMATION_PROGRESS, RenderStage.AUTOMATION)
    sample_count = len(next(iter(layers.values())))
    curves = build_automation(timeline, settings, sample_count, sample_rate)

    mix_rng = np.random.default_rng(settings.seed + MIX_SEED_OFFSET)
    stereo = mix(layers, curves, settings, mix_rng, sample_rate, reporter)
    return stereo, timeline


def render_track(
    settings: TrackSettings, reporter: ProgressReporter, sample_rate: int = SAMPLE_RATE
) -> RenderResult:
    """Produit le morceau décrit par les paramètres et l'écrit sur disque."""
    settings = settings.clamped()
    stereo, timeline = render_stereo(settings, reporter, sample_rate)

    reporter.report(WRITING_PROGRESS, RenderStage.WRITING)
    write_wave(settings.output_path, stereo, sample_rate)

    reporter.report(DONE_PROGRESS, RenderStage.DONE)
    return RenderResult(
        output_path=settings.output_path,
        duration=stereo.shape[1] / sample_rate,
        section_count=len(timeline.spans),
        event_count=len(timeline.events),
    )
