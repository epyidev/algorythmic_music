"""
Automation de mixage : gain, largeur stéréo et niveau de réverbération,
échantillon par échantillon.

Les trois courbes sont posées en marches, une valeur par section, puis
adoucies aux frontières. Sans ce lissage, passer d'une rupture à un climax
fait bondir le gain d'un facteur sept en un échantillon, ce qui s'entend
comme un coup sec et non comme une relance.

@author epyidev
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import oaconvolve

from ..config.track_settings import TrackSettings
from .timeline import Timeline

FADE_IN_EXPONENT = 1.5
FADE_IN_FLOOR = 0.05
FADE_OUT_EXPONENT = 1.7
MAX_REVERB_WET = 1.5
MAX_STEREO_WIDTH = 1.0
MIN_BLEND_SAMPLES = 3


@dataclass(frozen=True)
class AutomationCurves:
    """Les trois courbes que le mixage suit tout au long du morceau."""

    gain: np.ndarray
    stereo_width: np.ndarray
    reverb_wet: np.ndarray


def _blend(curve: np.ndarray, blend_samples: int) -> np.ndarray:
    """Adoucit les marches d'une courbe d'automation.

    Une fenêtre de Hann normalisée en moyenne glissante : la valeur au coeur
    d'une section reste exactement celle demandée, seules les frontières sont
    étalées sur la durée du fondu.
    """
    if blend_samples < MIN_BLEND_SAMPLES:
        return curve
    window = np.hanning(blend_samples)
    window /= window.sum()
    # Les bords sont prolongés, sinon le lissage creuse un trou au début et à la fin.
    padded = np.pad(curve, (blend_samples, blend_samples), mode="edge")
    return oaconvolve(padded, window, mode="same")[blend_samples:-blend_samples]


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

    blend_samples = int(settings.section_blend * sample_rate)
    return AutomationCurves(
        gain=_blend(gain, blend_samples),
        stereo_width=_blend(stereo_width, blend_samples),
        reverb_wet=_blend(reverb_wet, blend_samples),
    )
