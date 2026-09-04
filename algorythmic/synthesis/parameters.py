"""
Description d'un réglage numérique exposé à l'utilisateur.

Les timbres et les effets déclarent leurs réglages sous cette forme, et
l'interface construit ses curseurs à partir de cette déclaration. Ajouter un
réglage à un effet ne demande donc aucune retouche de l'interface.

@author epyidev
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Parameter:
    """Un réglage nommé, borné, avec sa valeur de départ."""

    name: str
    label: str
    minimum: float
    maximum: float
    default: float
    unit: str = ""
    decimals: int = 2

    def clamp(self, value: float) -> float:
        """Ramène une valeur dans les bornes du réglage."""
        return max(self.minimum, min(self.maximum, float(value)))


def default_values(parameters: tuple[Parameter, ...]) -> dict[str, float]:
    """Rend le jeu de valeurs de départ d'une liste de réglages."""
    return {parameter.name: parameter.default for parameter in parameters}


def resolve(
    parameters: tuple[Parameter, ...], values: dict[str, float]
) -> dict[str, float]:
    """Complète les valeurs manquantes et borne celles qui sont fournies."""
    return {
        parameter.name: parameter.clamp(values.get(parameter.name, parameter.default))
        for parameter in parameters
    }
