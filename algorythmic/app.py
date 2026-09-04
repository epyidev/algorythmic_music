"""
Démarrage de l'application graphique.

Le câblage est volontairement explicite : une application Qt, une fenêtre,
une boucle d'événements. Rien ne se charge tout seul.

@author epyidev
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from . import APPLICATION_NAME, APPLICATION_VERSION
from .ui.main_window import MainWindow


def run() -> int:
    """Ouvre la fenêtre et rend le code de sortie de la boucle d'événements."""
    application = QApplication(sys.argv)
    application.setApplicationName(APPLICATION_NAME)
    application.setApplicationVersion(APPLICATION_VERSION)

    window = MainWindow()
    window.show()
    return application.exec()
