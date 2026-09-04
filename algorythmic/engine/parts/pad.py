"""
Nappe : l'accord tenu, présent dans toutes les sections.

C'est la seule couche qui ne dépend pas de la densité : elle tient le morceau
même quand tout le reste se retire.

@author epyidev
"""

from __future__ import annotations

import numpy as np

from ...model.scale import SEMITONES_PER_OCTAVE
from ...synthesis.voices import VoiceSpec, render_voice
from ..placement import place_signal
from ..timeline import ChordEvent
from .context import PartContext

PAD_SPEC = VoiceSpec(partial_count=6, decay_exponent=2.2, attack=0.28)
PAD_HIGHEST_OFFSET = 18
PAD_AMPLITUDE = 0.16
PAD_TAIL = 1.4
PAD_JITTER_SCALE = 0.5


class PadPart:
    """Empile les notes de l'accord dans un registre médium serré."""

    layer_name = "pad"

    def render(
        self,
        buffer: np.ndarray,
        event: ChordEvent,
        rng: np.random.Generator,
        context: PartContext,
    ) -> None:
        duration = context.slot_duration + PAD_TAIL
        for interval in event.chord.intervals:
            midi = event.chord.root_midi + interval
            while midi > context.tonic_midi + PAD_HIGHEST_OFFSET:
                midi -= SEMITONES_PER_OCTAVE
            amplitude = context.timing.amplitude(rng, PAD_AMPLITUDE)
            offset = context.timing.offset(rng, PAD_JITTER_SCALE)
            place_signal(
                buffer,
                render_voice(midi, duration, rng, PAD_SPEC, context.sample_rate,
                             context.layer.timbre)
                * amplitude,
                event.start_time + offset,
                context.sample_rate,
            )
