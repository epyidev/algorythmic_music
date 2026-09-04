"""
Structure du morceau : la suite des sections et ce que chacune impose au mixage.

La densité pilote quelles couches jouent. La largeur stéréo lui est
volontairement inverse : quand l'orchestration se vide, l'image s'ouvre.

@author epyidev
"""

from __future__ import annotations

from dataclasses import dataclass

BEATS_PER_CELL = 8


@dataclass(frozen=True)
class Section:
    """Un bloc du morceau, avec ses réglages de mixage et d'orchestration."""

    name: str
    label: str
    cell_count: int
    gain: float
    density: float
    stereo_width: float
    reverb_wet: float
    lead_silence: float = 0.0
    has_melody: bool = True
    melody_octave_shift: int = 0
    fade_in: bool = False
    fade_out: bool = False


STANDARD_STRUCTURE = (
    Section("intro", "Intro", 4, 0.30, 0.25, 0.30, 0.55,
            has_melody=False, fade_in=True),
    Section("theme_a", "Thème A", 8, 0.80, 0.55, 0.24, 0.42),
    Section("theme_b", "Thème B", 12, 1.00, 0.90, 0.08, 0.30, lead_silence=0.20),
    Section("theme_c", "Thème C", 8, 1.00, 0.80, 0.10, 0.32, lead_silence=0.20),
    Section("break", "Rupture", 7, 0.17, 0.20, 0.30, 0.60),
    Section("climax", "Climax", 11, 1.27, 1.00, 0.11, 0.34,
            lead_silence=1.90, melody_octave_shift=1),
    Section("outro", "Outro", 3, 0.55, 0.30, 0.26, 0.55,
            has_melody=False, fade_out=True),
)

SHORT_STRUCTURE = (
    Section("intro", "Intro", 3, 0.32, 0.25, 0.30, 0.55,
            has_melody=False, fade_in=True),
    Section("theme_a", "Thème A", 6, 0.85, 0.60, 0.20, 0.40),
    Section("theme_b", "Thème B", 8, 1.00, 0.90, 0.09, 0.30, lead_silence=0.20),
    Section("outro", "Outro", 3, 0.50, 0.30, 0.26, 0.55,
            has_melody=False, fade_out=True),
)

LONG_STRUCTURE = STANDARD_STRUCTURE + (
    Section("reprise", "Reprise", 9, 0.90, 0.70, 0.18, 0.44, lead_silence=0.60),
    Section("coda", "Coda", 5, 0.45, 0.25, 0.30, 0.62,
            has_melody=False, fade_out=True),
)

STRUCTURES: dict[str, tuple[Section, ...]] = {
    "standard": STANDARD_STRUCTURE,
    "short": SHORT_STRUCTURE,
    "long": LONG_STRUCTURE,
}

STRUCTURE_LABELS: dict[str, str] = {
    "standard": "Standard (7 sections)",
    "short": "Court (4 sections)",
    "long": "Long (9 sections)",
}

DEFAULT_STRUCTURE = "standard"


def structure_sections(structure_name: str) -> tuple[Section, ...]:
    """Rend les sections de la structure demandée."""
    if structure_name not in STRUCTURES:
        raise KeyError(f"unknown structure: {structure_name}")
    return STRUCTURES[structure_name]
