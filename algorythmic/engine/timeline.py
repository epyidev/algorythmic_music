"""
Grille temporelle : où commence chaque section et où tombe chaque accord.

Les coupes franches sont un silence numérique inséré avant une section. Leur
durée est dosable, jusqu'à zéro pour un enchaînement continu.

@author epyidev
"""

from __future__ import annotations

from dataclasses import dataclass

from ..config.track_settings import TrackSettings
from ..model.arrangement import BEATS_PER_CELL, Section, structure_sections
from ..model.progression import Chord

LEAD_IN_SILENCE = 2.0
TAIL_SILENCE = 4.0


@dataclass(frozen=True)
class ChordEvent:
    """Un accord de la boucle, situé dans le temps et dans une section."""

    chord: Chord
    section: Section
    start_time: float
    cell_index: int
    slot_index: int


@dataclass(frozen=True)
class SectionSpan:
    """L'intervalle occupé par une section, silence de tête exclu."""

    section: Section
    start_time: float
    end_time: float


@dataclass(frozen=True)
class Timeline:
    """Tout le déroulé du morceau, prêt à être parcouru par les parties."""

    events: tuple[ChordEvent, ...]
    spans: tuple[SectionSpan, ...]
    duration: float
    slot_duration: float


def build_timeline(
    settings: TrackSettings,
    progression: tuple[Chord, ...],
    sections: tuple[Section, ...] | None = None,
    lead_in: float = LEAD_IN_SILENCE,
    tail: float = TAIL_SILENCE,
) -> Timeline:
    """Déroule la structure et place chaque accord sur l'axe du temps."""
    if sections is None:
        sections = structure_sections(settings.structure_name)

    beat = settings.beat_duration
    cell_duration = BEATS_PER_CELL * beat
    slot_duration = cell_duration / len(progression)

    events: list[ChordEvent] = []
    spans: list[SectionSpan] = []
    cursor = lead_in

    for section in sections:
        cursor += section.lead_silence * settings.hard_cut_amount
        section_start = cursor

        for cell_index in range(section.cell_count):
            cell_start = cursor + cell_index * cell_duration
            for slot_index, chord in enumerate(progression):
                events.append(ChordEvent(
                    chord=chord,
                    section=section,
                    start_time=cell_start + slot_index * slot_duration,
                    cell_index=cell_index,
                    slot_index=slot_index,
                ))

        cursor += section.cell_count * cell_duration
        spans.append(SectionSpan(section, section_start, cursor))

    return Timeline(
        events=tuple(events),
        spans=tuple(spans),
        duration=cursor + tail,
        slot_duration=slot_duration,
    )
