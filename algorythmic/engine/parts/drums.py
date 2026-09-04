"""
Percussions : présentes uniquement dans les sections les plus denses.

Elles ne tombent jamais sur la grille exacte, comme tout le reste.

@author epyidev
"""

from __future__ import annotations

import numpy as np

from ...synthesis.percussion import render_kick, render_tick
from ..placement import place_signal
from ..timeline import ChordEvent
from .context import PartContext

DRUMS_MIN_DENSITY = 0.7
STEPS_PER_CHORD = 4
KICK_SLOT_PERIOD = 2
KICK_STEP = 0
KICK_DURATION = 0.5
KICK_AMPLITUDE = 0.34
TICK_STEP = 2
TICK_CHANCE = 0.8
TICK_DURATION = 0.25
TICK_AMPLITUDE = 0.20


class DrumsPart:
    """Une grosse caisse un accord sur deux, un contretemps presque à chaque fois."""

    layer_name = "drums"

    def render(
        self,
        buffer: np.ndarray,
        event: ChordEvent,
        rng: np.random.Generator,
        context: PartContext,
    ) -> None:
        if event.section.density <= DRUMS_MIN_DENSITY:
            return

        step_duration = context.slot_duration / STEPS_PER_CHORD
        for step in range(STEPS_PER_CHORD):
            when = event.start_time + step * step_duration + context.timing.offset(rng)

            if step == KICK_STEP and event.slot_index % KICK_SLOT_PERIOD == 0:
                signal = render_kick(KICK_DURATION, context.sample_rate)
                place_signal(buffer, signal * KICK_AMPLITUDE, when, context.sample_rate)
            elif step == TICK_STEP and rng.random() < TICK_CHANCE:
                signal = render_tick(TICK_DURATION, rng, context.sample_rate)
                place_signal(buffer, signal * TICK_AMPLITUDE, when, context.sample_rate)
