"""
Basse : la fondamentale de l'accord, une octave sous la nappe.

@author epyidev
"""

from __future__ import annotations

import numpy as np

from ...model.scale import SEMITONES_PER_OCTAVE
from ...synthesis.voice import VoiceSpec, render_voice
from ..placement import place_signal
from ..timeline import ChordEvent
from .context import PartContext

BASS_SPEC = VoiceSpec(partial_count=5, decay_exponent=1.4, attack=0.05)
BASS_MIN_DENSITY = 0.3
BASS_AMPLITUDE = 0.30
BASS_TAIL = 0.5


class BassPart:
    """Une note par accord, absente des sections les plus clairsemées."""

    layer_name = "bass"

    def render(
        self,
        buffer: np.ndarray,
        event: ChordEvent,
        rng: np.random.Generator,
        context: PartContext,
    ) -> None:
        if event.section.density <= BASS_MIN_DENSITY:
            return

        midi = event.chord.root_midi - SEMITONES_PER_OCTAVE
        duration = context.slot_duration + BASS_TAIL
        place_signal(
            buffer,
            render_voice(midi, duration, rng, BASS_SPEC, context.sample_rate)
            * BASS_AMPLITUDE,
            event.start_time + context.timing.offset(rng),
            context.sample_rate,
        )
