#!/usr/bin/env python3
"""
Point d'entrée unique : interface graphique par défaut, ligne de commande
avec le drapeau dédié.

@author epyidev
"""

from __future__ import annotations

import sys

CLI_FLAG = "--cli"
CONSOLE_ENCODING = "utf-8"
CONSOLE_ERRORS = "replace"


def _force_console_encoding() -> None:
    """Évite qu'un accent fasse échouer un affichage sur une console héritée."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding=CONSOLE_ENCODING, errors=CONSOLE_ERRORS)


def main() -> int:
    """Choisit le front-end selon les arguments reçus."""
    _force_console_encoding()

    if CLI_FLAG in sys.argv:
        from algorythmic.cli import run as run_cli

        arguments = [value for value in sys.argv[1:] if value != CLI_FLAG]
        return run_cli(arguments)

    from algorythmic.app import run as run_gui

    return run_gui()


if __name__ == "__main__":
    sys.exit(main())
