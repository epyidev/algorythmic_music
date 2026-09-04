"""
Gammes modales et conversions de hauteur.

Une hauteur est toujours manipulée en numéro MIDI entier. La conversion en
hertz n'a lieu qu'au moment de la synthèse.

@author epyidev
"""

from __future__ import annotations

REFERENCE_MIDI = 69
REFERENCE_FREQUENCY = 440.0
SEMITONES_PER_OCTAVE = 12

MODE_INTERVALS: dict[str, tuple[int, ...]] = {
    "aeolian": (0, 2, 3, 5, 7, 8, 10),
    "dorian": (0, 2, 3, 5, 7, 9, 10),
    "phrygian": (0, 1, 3, 5, 7, 8, 10),
    "ionian": (0, 2, 4, 5, 7, 9, 11),
    "lydian": (0, 2, 4, 6, 7, 9, 11),
    "mixolydian": (0, 2, 4, 5, 7, 9, 10),
    "locrian": (0, 1, 3, 5, 6, 8, 10),
}

MODE_LABELS: dict[str, str] = {
    "aeolian": "Éolien (mineur naturel)",
    "dorian": "Dorien",
    "phrygian": "Phrygien",
    "ionian": "Ionien (majeur)",
    "lydian": "Lydien",
    "mixolydian": "Mixolydien",
    "locrian": "Locrien",
}

DEFAULT_MODE = "aeolian"

NOTE_NAMES = (
    "Do", "Do#", "Ré", "Ré#", "Mi", "Fa",
    "Fa#", "Sol", "Sol#", "La", "La#", "Si",
)

LOWEST_OCTAVE_OFFSET = -1


def midi_to_frequency(midi: float) -> float:
    """Rend la fréquence en hertz de la hauteur MIDI donnée."""
    exponent = (midi - REFERENCE_MIDI) / SEMITONES_PER_OCTAVE
    return REFERENCE_FREQUENCY * 2.0 ** exponent


def mode_intervals(mode_name: str) -> tuple[int, ...]:
    """Rend les degrés du mode, en demi-tons depuis la tonique."""
    if mode_name not in MODE_INTERVALS:
        raise KeyError(f"unknown mode: {mode_name}")
    return MODE_INTERVALS[mode_name]


def quantize_to_mode(midi: int, tonic_midi: int, mode_name: str) -> int:
    """Rabat une hauteur quelconque sur le degré le plus proche du mode."""
    intervals = mode_intervals(mode_name)
    relative = (midi - tonic_midi) % SEMITONES_PER_OCTAVE
    octave = (midi - tonic_midi) // SEMITONES_PER_OCTAVE
    nearest = min(intervals, key=lambda degree: abs(degree - relative))
    return tonic_midi + SEMITONES_PER_OCTAVE * octave + nearest


def note_label(midi: int) -> str:
    """Rend le nom français de la note, octave comprise."""
    name = NOTE_NAMES[midi % SEMITONES_PER_OCTAVE]
    octave = midi // SEMITONES_PER_OCTAVE + LOWEST_OCTAVE_OFFSET
    return f"{name}{octave}"
