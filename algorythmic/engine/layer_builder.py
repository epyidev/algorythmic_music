"""
Construction des couches instrumentales.

Chaque partie tire dans son propre flux aléatoire, dérivé de la graine du
morceau. Modifier une partie ne rebat donc pas les cartes des autres : deux
rendus qui ne diffèrent que par la densité gardent la même nappe.

@author epyidev
"""

from __future__ import annotations

import numpy as np

from ..config.track_settings import TrackSettings
from ..model.timing import build_timing
from .parts import BassPart, DrumsPart, MelodyPart, OstinatoPart, PadPart, PartContext
from .progress import ProgressReporter, RenderStage
from .timeline import Timeline

LAYER_PROGRESS_START = 0.04
LAYER_PROGRESS_END = 0.55
PROGRESS_EVENT_STRIDE = 16


def _build_parts(tonic_midi: int) -> tuple[object, ...]:
    """Instancie les parties dans l'ordre où elles écrivent leurs couches."""
    return (
        PadPart(),
        BassPart(),
        OstinatoPart(tonic_midi),
        MelodyPart(tonic_midi),
        DrumsPart(),
    )


def build_layers(
    settings: TrackSettings,
    timeline: Timeline,
    sample_rate: int,
    reporter: ProgressReporter,
) -> dict[str, np.ndarray]:
    """Rend une couche audio mono par partie instrumentale."""
    sample_count = int(timeline.duration * sample_rate)
    parts = _build_parts(settings.tonic_midi)
    layers = {part.layer_name: np.zeros(sample_count) for part in parts}

    seeds = np.random.SeedSequence(settings.seed).spawn(len(parts))
    streams = [np.random.default_rng(seed) for seed in seeds]

    context = PartContext(
        timing=build_timing(settings.beat_duration, settings.timing_looseness),
        sample_rate=sample_rate,
        tonic_midi=settings.tonic_midi,
        mode_name=settings.mode_name,
        slot_duration=timeline.events[1].start_time - timeline.events[0].start_time,
    )

    span = LAYER_PROGRESS_END - LAYER_PROGRESS_START
    for index, event in enumerate(timeline.events):
        for part, stream in zip(parts, streams):
            part.render(layers[part.layer_name], event, stream, context)
        if index % PROGRESS_EVENT_STRIDE == 0:
            ratio = LAYER_PROGRESS_START + span * index / len(timeline.events)
            reporter.report(ratio, RenderStage.LAYERS)

    return layers
