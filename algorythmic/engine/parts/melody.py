"""
Mélodie : des notes longues qui reviennent périodiquement sur le degré cinq.

Ce degré est mineur dans le mode choisi par défaut, donc dépourvu de
sensible. La mélodie y retombe sans jamais résoudre, et c'est exactement
l'effet recherché.

@author epyidev
"""

from __future__ import annotations

import numpy as np

from ...model.progression import dominant_root
from ...model.scale import SEMITONES_PER_OCTAVE
from ...synthesis.voice import VoiceSpec, render_voice
from ..placement import place_signal
from ..timeline import ChordEvent
from .context import PartContext

MELODY_SPEC = VoiceSpec(partial_count=5, decay_exponent=2.4, attack=0.09)
MELODY_LOWEST_OFFSET = 7
MELODY_HIGHEST_OFFSET = 26
MELODY_START_OFFSET = 14
MAX_LEAP_SEMITONES = 5
MELODY_AMPLITUDE = 0.13
MELODY_LENGTH_RATIO = 1.3
PLAYED_SLOT_PERIOD = 2
PIVOT_CELL_PERIOD = 4
PIVOT_CELL_INDEX = 3


class MelodyPart:
    """Alterne marche aléatoire dans l'accord et retour sur la note pivot."""

    layer_name = "melody"

    def __init__(self, tonic_midi: int) -> None:
        self._previous_midi = tonic_midi + MELODY_START_OFFSET

    def render(
        self,
        buffer: np.ndarray,
        event: ChordEvent,
        rng: np.random.Generator,
        context: PartContext,
    ) -> None:
        section = event.section
        if not section.has_melody:
            return
        if event.slot_index % PLAYED_SLOT_PERIOD != 0:
            return

        if event.cell_index % PIVOT_CELL_PERIOD == PIVOT_CELL_INDEX:
            midi = dominant_root(context.tonic_midi, context.mode_name)
            midi += SEMITONES_PER_OCTAVE * section.melody_octave_shift
        else:
            pool = event.chord.tones_in_range(
                context.tonic_midi + MELODY_LOWEST_OFFSET,
                context.tonic_midi + MELODY_HIGHEST_OFFSET,
            )
            if not pool:
                return
            reachable = [
                candidate for candidate in pool
                if abs(candidate - self._previous_midi) <= MAX_LEAP_SEMITONES
            ]
            midi = int(rng.choice(reachable if reachable else pool))

        self._previous_midi = midi
        place_signal(
            buffer,
            render_voice(
                midi,
                context.slot_duration * MELODY_LENGTH_RATIO,
                rng,
                MELODY_SPEC,
                context.sample_rate,
            ) * MELODY_AMPLITUDE,
            event.start_time + context.timing.offset(rng),
            context.sample_rate,
        )
