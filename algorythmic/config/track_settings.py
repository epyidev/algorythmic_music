"""
Paramètres d'un rendu, tels que l'interface les collecte et que le moteur
les consomme.

Le jeu de valeurs par défaut reproduit le morceau d'origine : même tonique,
même mode, même tempo, même structure.

@author epyidev
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from ..model.arrangement import DEFAULT_STRUCTURE
from ..model.scale import DEFAULT_MODE

SECONDS_PER_MINUTE = 60.0

MIN_SEED = 0
MAX_SEED = 999_999_999
DEFAULT_SEED = 42

MIN_TONIC_MIDI = 45
MAX_TONIC_MIDI = 68
DEFAULT_TONIC_MIDI = 56

MIN_BPM = 60.0
MAX_BPM = 180.0
DEFAULT_BPM = 117.5

MIN_AMOUNT = 0.0
MAX_AMOUNT = 2.0
DEFAULT_AMOUNT = 1.0

DEFAULT_OUTPUT_NAME = "morceau.wav"


def _clamp(value: float, lowest: float, highest: float) -> float:
    return max(lowest, min(highest, value))


@dataclass(frozen=True)
class TrackSettings:
    """Tout ce qui distingue un rendu d'un autre."""

    seed: int = DEFAULT_SEED
    tonic_midi: int = DEFAULT_TONIC_MIDI
    mode_name: str = DEFAULT_MODE
    bpm: float = DEFAULT_BPM
    structure_name: str = DEFAULT_STRUCTURE
    spectral_tilt: float = DEFAULT_AMOUNT
    reverb_amount: float = DEFAULT_AMOUNT
    stereo_width: float = DEFAULT_AMOUNT
    timing_looseness: float = DEFAULT_AMOUNT
    output_path: Path = Path(DEFAULT_OUTPUT_NAME)

    @property
    def beat_duration(self) -> float:
        """Durée d'un temps, en secondes."""
        return SECONDS_PER_MINUTE / self.bpm

    def clamped(self) -> "TrackSettings":
        """Rend une copie dont toutes les valeurs numériques sont dans les bornes."""
        return replace(
            self,
            seed=int(_clamp(self.seed, MIN_SEED, MAX_SEED)),
            tonic_midi=int(_clamp(self.tonic_midi, MIN_TONIC_MIDI, MAX_TONIC_MIDI)),
            bpm=_clamp(self.bpm, MIN_BPM, MAX_BPM),
            spectral_tilt=_clamp(self.spectral_tilt, MIN_AMOUNT, MAX_AMOUNT),
            reverb_amount=_clamp(self.reverb_amount, MIN_AMOUNT, MAX_AMOUNT),
            stereo_width=_clamp(self.stereo_width, MIN_AMOUNT, MAX_AMOUNT),
            timing_looseness=_clamp(self.timing_looseness, MIN_AMOUNT, MAX_AMOUNT),
        )
