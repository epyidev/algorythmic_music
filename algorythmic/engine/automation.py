"""
Automation de mixage : gain, largeur stéréo et niveau de réverbération,
échantillon par échantillon.

@author epyidev
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..config.track_settings import TrackSettings
from .timeline import Timeline

FADE_IN_EXPONENT = 1.5
FADE_IN_FLOOR = 0.05
FADE_OUT_EXPONENT = 1.7
MAX_REVERB_WET = 1.5
MAX_STEREO_WIDTH = 1.0


@dataclass(frozen=True)
class AutomationCurves:
    """Les trois courbes que le mixage suit tout au long du morceau."""

    gain: np.ndarray
    stereo_width: np.ndarray
    reverb_wet: np.ndarray


def build_automation(
    timeline: Timeline,
    settings: TrackSettings,
    sample_count: int,
    sample_rate: int,
) -> AutomationCurves:
    """Déplie les réglages de chaque section sur l'axe des échantillons."""
    gain = np.zeros(sample_count)
    stereo_width = np.zeros(sample_count)
    reverb_wet = np.zeros(sample_count)

    for span in timeline.spans:
        start = int(span.start_time * sample_rate)
        end = min(int(span.end_time * sample_rate), sample_count)
        if end <= start:
            continue

        section = span.section
        segment = np.full(end - start, section.gain)
        if section.fade_in:
            segment *= np.linspace(FADE_IN_FLOOR, 1.0, end - start) ** FADE_IN_EXPONENT
        if section.fade_out:
            segment *= np.linspace(1.0, 0.0, end - start) ** FADE_OUT_EXPONENT

        gain[start:end] = segment
        stereo_width[start:end] = min(
            section.stereo_width * settings.stereo_width, MAX_STEREO_WIDTH
        )
        reverb_wet[start:end] = min(
            section.reverb_wet * settings.reverb_amount, MAX_REVERB_WET
        )

    return AutomationCurves(gain, stereo_width, reverb_wet)
