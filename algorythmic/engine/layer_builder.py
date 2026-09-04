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
from ..model.layers import BASS, DRUMS, MELODY, OSTINATO, PAD
from ..model.timing import build_timing
from ..synthesis.effects import apply_chain
from .parts import BassPart, DrumsPart, MelodyPart, OstinatoPart, PadPart, PartContext
from .progress import ProgressReporter, RenderStage
from .timeline import Timeline

LAYER_PROGRESS_START = 0.04
LAYER_PROGRESS_END = 0.50
EFFECTS_PROGRESS_END = 0.55
PROGRESS_EVENT_STRIDE = 16
LEVEL_GUARD = 1e-12


def _build_parts(tonic_midi: int) -> tuple[object, ...]:
    """Instancie les parties dans l'ordre où elles écrivent leurs couches."""
    return (
        PadPart(),
        BassPart(),
        OstinatoPart(tonic_midi),
        MelodyPart(tonic_midi),
        DrumsPart(),
    )


def _layer_order() -> tuple[str, ...]:
    return (PAD, BASS, OSTINATO, MELODY, DRUMS)


def build_layers(
    settings: TrackSettings,
    timeline: Timeline,
    sample_rate: int,
    reporter: ProgressReporter,
) -> dict[str, np.ndarray]:
    """Rend une couche audio mono par partie instrumentale, effets compris."""
    sample_count = int(timeline.duration * sample_rate)
    parts = _build_parts(settings.tonic_midi)
    layers = {part.layer_name: np.zeros(sample_count) for part in parts}

    seeds = np.random.SeedSequence(settings.seed).spawn(len(parts))
    streams = [np.random.default_rng(seed) for seed in seeds]

    timing = build_timing(settings.beat_duration, settings.timing_looseness)
    contexts = [
        PartContext(
            timing=timing,
            sample_rate=sample_rate,
            tonic_midi=settings.tonic_midi,
            mode_name=settings.mode_name,
            slot_duration=timeline.slot_duration,
            layer=settings.layer(part.layer_name),
        )
        for part in parts
    ]

    span = LAYER_PROGRESS_END - LAYER_PROGRESS_START
    for index, event in enumerate(timeline.events):
        for part, stream, context in zip(parts, streams, contexts):
            if not context.layer.enabled:
                continue
            part.render(layers[part.layer_name], event, stream, context)
        if index % PROGRESS_EVENT_STRIDE == 0:
            ratio = LAYER_PROGRESS_START + span * index / len(timeline.events)
            reporter.report(ratio, RenderStage.LAYERS)

    return _process_layers(layers, settings, sample_rate, reporter)


def _process_layers(
    layers: dict[str, np.ndarray],
    settings: TrackSettings,
    sample_rate: int,
    reporter: ProgressReporter,
) -> dict[str, np.ndarray]:
    """Applique la chaîne d'effets et le niveau de chaque couche."""
    keys = _layer_order()
    span = EFFECTS_PROGRESS_END - LAYER_PROGRESS_END

    for index, key in enumerate(keys):
        reporter.report(
            LAYER_PROGRESS_END + span * index / len(keys), RenderStage.EFFECTS
        )
        layer = settings.layer(key)
        if not layer.enabled:
            layers[key] = np.zeros_like(layers[key])
            continue

        signal = layers[key]
        if layer.effects and np.max(np.abs(signal)) > LEVEL_GUARD:
            signal = apply_chain(signal, sample_rate, layer.effects)
        layers[key] = signal * layer.gain

    return layers
