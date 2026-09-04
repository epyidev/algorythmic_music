"""
Mode sans interface, pour enchaîner des rendus depuis un terminal.

La progression est réécrite sur la même ligne, comme dans la fenêtre.

@author epyidev
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .config.track_settings import (
    DEFAULT_BPM,
    DEFAULT_OUTPUT_NAME,
    DEFAULT_SEED,
    DEFAULT_TONIC_MIDI,
    MAX_BPM,
    MAX_TONIC_MIDI,
    MIN_BPM,
    MIN_TONIC_MIDI,
    TrackSettings,
)
from .engine.progress import ProgressReporter, RenderCancelled, RenderStage
from .engine.renderer import render_track
from .model.arrangement import DEFAULT_STRUCTURE, STRUCTURE_LABELS, STRUCTURES
from .model.scale import DEFAULT_MODE, MODE_INTERVALS, MODE_LABELS, note_label
from .texts import (
    CLI_DESCRIPTION,
    CLI_HELP_MODE,
    CLI_HELP_OUTPUT,
    CLI_HELP_SEED,
    CLI_HELP_STRUCTURE,
    CLI_HELP_TEMPO,
    CLI_HELP_TONIC,
    CLI_PROGRESS,
    LOG_CANCELLED,
    LOG_DURATION,
    LOG_FINISHED,
    LOG_STARTED,
    LOG_STRUCTURE,
    STAGE_LABELS,
)

PERCENT_SCALE = 100
SECONDS_PER_MINUTE = 60


def build_parser() -> argparse.ArgumentParser:
    """Décrit les options acceptées en ligne de commande."""
    parser = argparse.ArgumentParser(description=CLI_DESCRIPTION)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help=CLI_HELP_SEED)
    parser.add_argument(
        "--tonic",
        type=int,
        default=DEFAULT_TONIC_MIDI,
        choices=range(MIN_TONIC_MIDI, MAX_TONIC_MIDI + 1),
        metavar=f"[{MIN_TONIC_MIDI}-{MAX_TONIC_MIDI}]",
        help=CLI_HELP_TONIC,
    )
    parser.add_argument(
        "--mode",
        default=DEFAULT_MODE,
        choices=sorted(MODE_INTERVALS),
        help=CLI_HELP_MODE,
    )
    parser.add_argument("--bpm", type=float, default=DEFAULT_BPM, help=CLI_HELP_TEMPO)
    parser.add_argument(
        "--structure",
        default=DEFAULT_STRUCTURE,
        choices=sorted(STRUCTURES),
        help=CLI_HELP_STRUCTURE,
    )
    parser.add_argument(
        "--out", type=Path, default=Path(DEFAULT_OUTPUT_NAME), help=CLI_HELP_OUTPUT
    )
    return parser


def _print_progress(ratio: float, stage: RenderStage) -> None:
    percent = int(ratio * PERCENT_SCALE)
    line = CLI_PROGRESS.format(percent=percent, stage=STAGE_LABELS[stage])
    print(line.ljust(PERCENT_SCALE // 2), end="\r", flush=True)


def run(argv: list[str] | None = None) -> int:
    """Lance un rendu depuis le terminal et rend le code de sortie."""
    arguments = build_parser().parse_args(argv)
    settings = TrackSettings(
        seed=arguments.seed,
        tonic_midi=arguments.tonic,
        mode_name=arguments.mode,
        bpm=max(min(arguments.bpm, MAX_BPM), MIN_BPM),
        structure_name=arguments.structure,
        output_path=arguments.out,
    ).clamped()

    print(LOG_STARTED.format(
        seed=settings.seed,
        tonic=note_label(settings.tonic_midi),
        mode=MODE_LABELS[settings.mode_name],
        bpm=settings.bpm,
    ))

    try:
        result = render_track(settings, ProgressReporter(_print_progress))
    except RenderCancelled:
        print(LOG_CANCELLED)
        return 1

    minutes, seconds = divmod(int(result.duration), SECONDS_PER_MINUTE)
    print()
    print(LOG_STRUCTURE.format(
        structure=STRUCTURE_LABELS[settings.structure_name],
        sections=result.section_count,
        events=result.event_count,
    ))
    print(LOG_DURATION.format(minutes=minutes, seconds=seconds))
    print(LOG_FINISHED.format(path=result.output_path))
    return 0
