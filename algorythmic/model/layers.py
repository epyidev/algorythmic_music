"""
Les couches du morceau, leur ordre et leur nom.

@author epyidev
"""

from __future__ import annotations

PAD = "pad"
BASS = "bass"
OSTINATO = "ostinato"
MELODY = "melody"
DRUMS = "drums"

LAYER_KEYS = (PAD, BASS, OSTINATO, MELODY, DRUMS)

LAYER_LABELS: dict[str, str] = {
    PAD: "Nappe",
    BASS: "Basse",
    OSTINATO: "Ostinato",
    MELODY: "Mélodie",
    DRUMS: "Percussions",
}

# Les percussions sont synthétisées à part : elles n'ont pas de timbre à choisir.
LAYERS_WITH_TIMBRE = (PAD, BASS, OSTINATO, MELODY)
