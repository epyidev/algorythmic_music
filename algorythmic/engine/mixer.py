"""
Mixage : somme des couches, réverbération, basculement spectral, stéréo,
dynamique.

L'ordre compte. Le basculement spectral vient après la réverbération et
s'applique de façon identique aux deux canaux, sinon il déforme l'image
stéréo au lieu de colorer le mixage.

@author epyidev
"""

from __future__ import annotations

import numpy as np

from ..config.track_settings import TrackSettings
from ..synthesis.dynamics import finalise
from ..synthesis.reverb import build_impulse_response, convolve_tail
from ..synthesis.spectral_tilt import apply_tilt, build_tilt_filter
from ..synthesis.stereo import apply_width
from .automation import AutomationCurves
from .progress import ProgressReporter, RenderStage

REVERB_PROGRESS = 0.62
TILT_PROGRESS = 0.78
STEREO_PROGRESS = 0.88
DYNAMICS_PROGRESS = 0.94
REVERB_MAKEUP_GAIN = 1.5
LEVEL_GUARD = 1e-9


def mix(
    layers: dict[str, np.ndarray],
    curves: AutomationCurves,
    settings: TrackSettings,
    rng: np.random.Generator,
    sample_rate: int,
    reporter: ProgressReporter,
) -> np.ndarray:
    """Rend le mixage stéréo final, prêt à être écrit sur disque."""
    dry = sum(layers.values()) * curves.gain
    dry_peak = np.max(np.abs(dry)) + LEVEL_GUARD

    reporter.report(REVERB_PROGRESS, RenderStage.REVERB)
    tail = build_impulse_response(rng, sample_rate)
    wet_gain = curves.reverb_wet * dry_peak * REVERB_MAKEUP_GAIN
    left = dry + wet_gain * convolve_tail(dry, tail[0])
    right = dry + wet_gain * convolve_tail(dry, tail[1])

    reporter.report(TILT_PROGRESS, RenderStage.SPECTRAL_TILT)
    kernel = build_tilt_filter(
        (left + right) / 2.0, sample_rate, settings.spectral_tilt
    )
    left, right = apply_tilt(left, kernel), apply_tilt(right, kernel)

    reporter.report(STEREO_PROGRESS, RenderStage.STEREO)
    left, right = apply_width(left, right, curves.stereo_width, sample_rate)

    reporter.report(DYNAMICS_PROGRESS, RenderStage.DYNAMICS)
    return finalise(np.stack([left, right]), sample_rate)
