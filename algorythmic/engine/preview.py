"""
Extrait court, rendu avec la chaîne complète, pour écouter un réglage sans
attendre le morceau entier.

La préécoute traverse exactement le même code que le rendu final : même
synthèse, mêmes effets, même mixage. Seule la grille change, réduite à deux
cellules d'une section dense et débarrassée de ses silences de tête et de
queue.

@author epyidev
"""

from __future__ import annotations

from dataclasses import dataclass

from ..audio_io.pcm import to_bytes
from ..config.audio_format import SAMPLE_RATE
from ..config.track_settings import TrackSettings
from ..model.arrangement import Section
from .progress import ProgressReporter, RenderStage
from .renderer import render_stereo

PREVIEW_SECTION = Section(
    name="preview",
    label="Préécoute",
    cell_count=2,
    gain=1.0,
    density=0.9,
    stereo_width=0.12,
    reverb_wet=0.34,
)
PREVIEW_LEAD_IN = 0.05
PREVIEW_TAIL = 1.4
DONE_PROGRESS = 1.0


@dataclass(frozen=True)
class PreviewResult:
    """L'extrait rendu, sous forme d'échantillons entrelacés."""

    frames: bytes
    duration: float
    sample_rate: int


def render_preview(
    settings: TrackSettings,
    reporter: ProgressReporter,
    sample_rate: int = SAMPLE_RATE,
) -> PreviewResult:
    """Rend un extrait de quelques secondes avec les réglages courants."""
    stereo, _ = render_stereo(
        settings.clamped(),
        reporter,
        sample_rate,
        sections=(PREVIEW_SECTION,),
        lead_in=PREVIEW_LEAD_IN,
        tail=PREVIEW_TAIL,
    )
    reporter.report(DONE_PROGRESS, RenderStage.DONE)
    return PreviewResult(
        frames=to_bytes(stereo),
        duration=stereo.shape[1] / sample_rate,
        sample_rate=sample_rate,
    )
