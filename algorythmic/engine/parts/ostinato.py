"""
Ostinato : des croches qui se promènent dans l'accord.

La marche est aléatoire mais bornée : jamais plus d'une quinte entre deux
notes, ce qui donne une ligne qui tourne sans jamais partir ailleurs.

@author epyidev
"""

from __future__ import annotations

import numpy as np

from ...synthesis.voices import VoiceSpec, render_voice
from ..placement import place_signal
from ..timeline import ChordEvent
from .context import PartContext

OSTINATO_SPEC = VoiceSpec(partial_count=8, decay_exponent=1.6, attack=0.014)
OSTINATO_LOWEST_OFFSET = 12
OSTINATO_HIGHEST_OFFSET = 33
OSTINATO_START_OFFSET = 19
MAX_LEAP_SEMITONES = 7
NOTES_PER_CHORD = 4
BASE_PLAY_CHANCE = 0.55
DENSITY_PLAY_CHANCE = 0.45
OSTINATO_AMPLITUDE = 0.11
OSTINATO_FLOOR_GAIN = 0.6
OSTINATO_DENSITY_GAIN = 0.4
OSTINATO_TAIL = 0.55


class OstinatoPart:
    """Garde la dernière note jouée pour contraindre le saut suivant."""

    layer_name = "ostinato"

    def __init__(self, tonic_midi: int) -> None:
        self._previous_midi = tonic_midi + OSTINATO_START_OFFSET

    def render(
        self,
        buffer: np.ndarray,
        event: ChordEvent,
        rng: np.random.Generator,
        context: PartContext,
    ) -> None:
        density = event.section.density
        pool = event.chord.tones_in_range(
            context.tonic_midi + OSTINATO_LOWEST_OFFSET,
            context.tonic_midi + OSTINATO_HIGHEST_OFFSET,
        )
        if not pool:
            return

        step_duration = context.slot_duration / NOTES_PER_CHORD
        play_chance = BASE_PLAY_CHANCE + DENSITY_PLAY_CHANCE * density

        for step in range(NOTES_PER_CHORD):
            if rng.random() > play_chance:
                continue

            reachable = [
                midi for midi in pool
                if abs(midi - self._previous_midi) <= MAX_LEAP_SEMITONES
            ]
            self._previous_midi = int(rng.choice(reachable if reachable else pool))

            gain = OSTINATO_FLOOR_GAIN + OSTINATO_DENSITY_GAIN * density
            amplitude = context.timing.amplitude(rng, OSTINATO_AMPLITUDE) * gain
            place_signal(
                buffer,
                render_voice(
                    self._previous_midi,
                    step_duration + OSTINATO_TAIL,
                    rng,
                    OSTINATO_SPEC,
                    context.sample_rate,
                    context.layer.timbre,
                ) * amplitude,
                event.start_time + step * step_duration + context.timing.offset(rng),
                context.sample_rate,
            )
