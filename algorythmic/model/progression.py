"""
Construction de la boucle harmonique à partir des degrés du mode.

Les accords ne sont pas écrits en dur : ils sont empilés par tierces sur la
gamme choisie, ce qui garde la couleur de la boucle quelle que soit la
tonique et quel que soit le mode.

@author epyidev
"""

from __future__ import annotations

from dataclasses import dataclass

from .scale import SEMITONES_PER_OCTAVE, mode_intervals

SEVENTH_STEPS = (0, 2, 4, 6)
PROGRESSION_DEGREES = (2, 4, 0, 4)
DOMINANT_DEGREE = 4
OCTAVE_SEARCH_RANGE = range(-3, 4)


@dataclass(frozen=True)
class Chord:
    """Un accord, donné par sa fondamentale et ses intervalles internes."""

    root_midi: int
    intervals: tuple[int, ...]

    def tones_in_range(self, lowest_midi: int, highest_midi: int) -> tuple[int, ...]:
        """Rend toutes les notes de l'accord comprises dans un registre."""
        tones = set()
        for octave in OCTAVE_SEARCH_RANGE:
            for interval in self.intervals:
                midi = self.root_midi + interval + SEMITONES_PER_OCTAVE * octave
                if lowest_midi <= midi <= highest_midi:
                    tones.add(midi)
        return tuple(sorted(tones))


def build_seventh_chord(degree_index: int, tonic_midi: int, mode_name: str) -> Chord:
    """Empile un accord de septième sur un degré du mode."""
    intervals = mode_intervals(mode_name)
    degree_count = len(intervals)
    root_offset = intervals[degree_index % degree_count]
    root_midi = tonic_midi + root_offset

    tones = []
    for step in SEVENTH_STEPS:
        index = degree_index + step
        octave = index // degree_count
        offset = intervals[index % degree_count] + SEMITONES_PER_OCTAVE * octave
        tones.append(offset - root_offset)
    return Chord(root_midi=root_midi, intervals=tuple(tones))


def build_progression(tonic_midi: int, mode_name: str) -> tuple[Chord, ...]:
    """Rend la boucle harmonique du morceau, un accord par demi-mesure."""
    return tuple(
        build_seventh_chord(degree, tonic_midi, mode_name)
        for degree in PROGRESSION_DEGREES
    )


def dominant_root(tonic_midi: int, mode_name: str) -> int:
    """Rend la fondamentale du degré sur lequel la mélodie revient sans cesse."""
    return tonic_midi + mode_intervals(mode_name)[DOMINANT_DEGREE]
